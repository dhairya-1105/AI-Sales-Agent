from llama_index.llms.groq import Groq
import sqlite3
import uuid
import json
from typing import List, Dict, Any
from datetime import datetime
from create_catalog import retrieve

class SalesAgent:
    def __init__(self, api_key: str):
        self.llm = Groq(api_key="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", model = "llama-3.3-70b-versatile", temperature = 0)
        self.init_database()
        self.conversation_active = True # For conversation state tracking
        self.waiting_for_name = False
        self.pending_order = None
        self.tools = {
            "search_catalog": self.search_catalog,
            "create_order": self.create_order,
            "end_tool" : self.end_tool
        }
        self.customer_info = {
            "budget": None,
            "preferences": [],
            "previous_recommendations": set(),
            "name": None
        }

    def init_database(self):
        conn = sqlite3.connect('sales_orders.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS orders
                     (order_id TEXT PRIMARY KEY,
                      customer_name TEXT,
                      product_info TEXT,
                      timestamp DATETIME)''')
        conn.commit()
        conn.close()

    def update_customer_info(self, response: str):
        """Extract and update customer information from the conversation"""
        # Check for budget mentions
        if "budget" in response.lower() and "$" in response:
            try:
                # Simple budget extraction - can be made more sophisticated
                budget_text = response[response.lower().find("budget"):]
                budget = ''.join(filter(str.isdigit, budget_text.split('\n')[0]))
                if budget:
                    self.customer_info["budget"] = int(budget)
            except:
                pass

        # Track recommended products
        if "[TOOL_CALL]search_catalog" in response:
            try:
                start = response.find("[TOOL_CALL]search_catalog")
                end = response.find("[/TOOL_CALL]", start)
                search_text = response[start:end]
                self.customer_info["previous_recommendations"].add(search_text)
            except:
                pass

    def search_catalog(self, query: str, detailed: bool = False) -> str:
        results = retrieve(query, k=3)
        raw_content = "\n".join([content for content, _ in results])
        
        # Include customer context in the refinement prompt
        context = ""
        if self.customer_info["budget"]:
            context += f"\nCustomer budget: ${self.customer_info['budget']}"
        if self.customer_info["preferences"]:
            context += f"\nCustomer preferences: {', '.join(self.customer_info['preferences'])}"
        
        refine_prompt = f"""Based on the following product information and customer context, provide a brief, focused summary.
            Take user query into account as well. Highlight only the most relevant points and maintain a conversational tone.
            Keep the response to 2-3 short sentences. It must feel like human speech and NOT a paragraph/essay.

            Customer Context:{context}
            Previous recommendations: {list(self.customer_info["previous_recommendations"])}

            Product Information:
            {raw_content}
            
            Query:
            {query}

            Provide a concise, customer-friendly summary focusing on products not previously recommended."""

        refined_response = self.llm.complete(refine_prompt)
        return refined_response.text
    
    def end_tool(self):
        """Generate a contextual farewell message"""
        context = ""
        if self.customer_info["name"]:
            context += f"\nCustomer name: {self.customer_info['name']}"
        if len(self.customer_info["previous_recommendations"]) > 0:
            context += "\nProducts were recommended during the conversation"
        
        farewell_prompt = f"""Generate a brief, friendly farewell message for a customer.
        Keep it natural and conversational. Include gratitude for their time.
        
        Context:{context}
        
        The message should be one or two short sentences."""
        
        farewell_response = self.llm.complete(farewell_prompt)
        self.conversation_active = False
        return farewell_response.text

    def create_order(self, product_info: str, customer_name :str) -> str:
        self.waiting_for_name = True
        self.pending_order = product_info
        self.customer_name = customer_name
        order_id = str(uuid.uuid4())
        conn = sqlite3.connect('sales_orders.db')
        c = conn.cursor()
        c.execute("""INSERT INTO orders (order_id, customer_name, product_info, timestamp)
                    VALUES (?, ?, ?, ?)""", 
                    (order_id, customer_name, self.pending_order, datetime.now()))
        conn.commit()
        conn.close()
        
        self.waiting_for_name = False
        self.pending_order = None
        self.customer_info["name"] = customer_name
        
        return f"Order created successfully! Order ID: {order_id}"

    
    # def complete_order(self, customer_name: str) -> str:
    #     if not self.pending_order:
    #         return "No pending order found."
        
        
    def parse_tool_parameters(self, params_str: str) -> Dict[str, Any]:
        """Safely parse tool parameters from string"""
        cleaned_params = params_str.replace("'", '"')
        cleaned_params = cleaned_params.replace("false", "false")
        cleaned_params = cleaned_params.replace("true", "true")
        
        try:
            return json.loads(cleaned_params)
        except json.JSONDecodeError:
            try:
                params_tuple = params_str.strip('()').split(',')
                if len(params_tuple) == 2:
                    return {
                        "customer_name": params_tuple[0].strip().strip("'\""),
                        "product_info": params_tuple[1].strip().strip("'\"")
                    }
            except Exception:
                pass
            return {}

    def generate_response(self, user_input: str, conversation_history: List[str]) -> str:
        # Include customer info in the system prompt
        context_info = "\nCurrent customer information:"
        if self.customer_info["budget"]:
            context_info += f"\n- Budget: ${self.customer_info['budget']}"
        if self.customer_info["preferences"]:
            context_info += f"\n- Preferences: {', '.join(self.customer_info['preferences'])}"
        if self.customer_info["previous_recommendations"]:
            context_info += f"\n- Previously recommended products: {list(self.customer_info['previous_recommendations'])}"

        system_prompt = f"""You are Mithali, helpful and knowledgeable human sales assistant who has cold called the customer trying to selling mattresses, nothing else. Your goal is to engage in natural conversation and help customers find the right products. Follow these guidelines:

1. Keep your responses concise and engaging. Never overwhelm the customer with information.

2. When handling general product queries:
   - Provide a brief overview
   - Ask about specific needs or preferences ONLY if not already known
   - Guide the conversation towards finding the right product match
   - Do not provide too much information at once, limit the response to a maximum of two short sentences

3. For specific product queries:
   - Focus on the most relevant features for that customer
   - Maintain a conversational human tone
   - Include pricing and key specifications only when asked
   - Do not create synthetic information, always use the search_catalog tool when you are providing information about something
   - Answer based on what the user asks for, don't provide unsolicited information
   - Do not mention anything about the stock availability or warranty
   - IMPORTANT: DO NOT ask about information you already have (check Current customer information section)
   - After creating the order, don't mention anything about payments
   - Always refer conversation history before asking any questions
   - If the user places an order, do not mention the order ID in your response

4. Use the available tools strategically:
   - search_catalog: Use with {{'query': 'search terms', 'detailed': false}} for browsing, {{'query': 'specific product', 'detailed': true}} for specific products
   - create_order: CALL ONLY AFTER THE CUSTOMER HAS PROVIDED THEIR NAME AND IS READY TO PURCHASE.  ('product_info': 'product name', 'customer_name':'customer name').
   - end_tool: Use when the conversation needs to end.

### Example Workflow

Assistant:
Hello, my name is Mithali. I'm calling from Sleep Haven Products. Would you be interested exploring our mattress options?

User:
I'm looking for a comfortable mattress for back pain. My budget is around $500.

Assistant:
I recommend checking out memory foam mattresses as they provide excellent support for back pain. Let me find some options within your budget.  
[TOOL_CALL]search_catalog: {{'query': 'memory foam mattress for back pain', 'detailed': false}}[/TOOL_CALL]

Tool Response (Search Catalog):
Here are some great options:  
1. Orthopedic Memory Foam Mattress : $450  
2. PosturePro Memory Foam Mattress : $400  
3. DreamSoft Back Support Mattress : $500  

Assistant:
Here are a few mattresses that match your needs:  
- Orthopedic Memory Foam Mattress ($450)  
- PosturePro Memory Foam Mattress ($400)  
- DreamSoft Back Support Mattress ($500)  

Do any of these interest you? Let me know if you'd like more details or recommendations!

User:
The DreamSoft Back Support Mattress sounds good. Can I place an order?

Assistant:
Great choice! I'll have to take your name to place the order. Please provide your name.

User: 
My name is Alex.

Assistant:
Let me create an order for the DreamSoft Back Support Mattress. 
[TOOL_CALL]create_order: {{'product_info': 'DreamSoft Back Support Mattress', 'customer_name':'Alex'}}[/TOOL_CALL]

Tool Response (Create Order):
Order created successfully! Order ID: abc123-xyz456

Assistant:
Your order for the DreamSoft Back Support Mattress has been placed successfully! Is there anything else I can assist you with?

User:
No, that's all. Thank you!

Assistant:
Thank you for shopping with us! Have a great day!  
[TOOL_CALL]end_tool:{{}}[/TOOL_CALL]



BEFORE CALLING ANY TOOL, CHECK IF THE USER QUERY CAN BE ANSWERED VIA THE INFORMATION ALREADY PRESENT IN THE CONVERSATION HISTORY.

{context_info}

Format tool calls as: [TOOL_CALL]<tool_name>: <parameters>[/TOOL_CALL]
"""

        # Include more conversation history for better context
        conversation_context = "\n".join(conversation_history[:])
        full_prompt = f"{system_prompt}\n\nConversation history:\n{conversation_context}\n\nCustomer: {user_input}\nAssistant:"

        response = self.llm.complete(full_prompt)
        processed_response = self.process_tool_calls(response.text)
        
        # Update customer info based on the response
        self.update_customer_info(processed_response)
        
        return processed_response

    def process_tool_calls(self, response: str) -> str:
        if "[TOOL_CALL]" not in response:
            return response

        processed_response = response
        while "[TOOL_CALL]" in processed_response:
            start = processed_response.find("[TOOL_CALL]")
            end = processed_response.find("[/TOOL_CALL]")
            if start == -1 or end == -1:
                break

            tool_call = processed_response[start + 11:end]
            try:
                tool_name, params = tool_call.split(":", 1) if ":" in tool_call else (tool_call.strip(), "")
                tool_name = tool_name.strip()
                params = params.strip()
            except ValueError:
                continue

            if tool_name in self.tools:
                try:
                    if tool_name == "search_catalog":
                        params_dict = self.parse_tool_parameters(params)
                        query = params_dict.get('query', '')
                        detailed = params_dict.get('detailed', False)
                        tool_response = self.tools[tool_name](query, detailed)
                    elif tool_name == "create_order":
                        params_dict = self.parse_tool_parameters(params)
                        product_info = params_dict.get('product_info', '')
                        customer_name = params_dict.get('customer_name', '')
                        tool_response = self.tools[tool_name](product_info, customer_name)
                    elif tool_name == "end_tool":
                        tool_response = self.tools[tool_name]()  # Call end_tool directly
                        self.conversation_active = False  # Ensure conversation state is updated
                    else:
                        tool_response = "\nTool not found."
                except Exception as e:
                    tool_response = f"\nError processing tool call: {str(e)}"
            else:
                tool_response = "\nTool not found."

            processed_response = processed_response[:start] + tool_response + processed_response[end + 13:]

        return processed_response

def main():
    agent = SalesAgent(api_key="your-groq-api-key")
    conversation_history = []
    
    while True:
        if not agent.conversation_active:  # Check conversation state
            break
            
        user_input = input("You: ")
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("AI Sales Assistant: Thank you for shopping with us! Goodbye!")
            break
            
        response = agent.generate_response(user_input, conversation_history)
        print("AI Sales Assistant:", response)
        
        conversation_history.extend([f"User: {user_input}", f"Assistant: {response}"])

if __name__ == "__main__":
    main()