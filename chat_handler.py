import json
from rag_retriever import ask_general

def load_script():
    with open("Calling Script.txt", "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

LINES = load_script()

class ChatHandler:
    def __init__(self):
        with open("customer_policies.json", "r", encoding="utf-8") as f:
            self.customers = json.load(f)
        self.step = 0
        self.customer = None

    def _find_customer(self, name):
        for c in self.customers:
            if name.lower() in c["name"].lower():
                return c
        return None

    def handle(self, msg: str) -> str:
        m = msg.strip().lower()             
        

    # ✅ Handle general insurance questions using RAG before flow
        if any(w in m for w in ["term insurance", "insurance", "policy", "premium", "benefit", "sum assured", "coverage", "claim"]):
             return ask_general(msg)

        # Step 0: Identify name
        if self.step == 0:
            for c in self.customers:
                if c["name"].lower() in m:
                    self.customer = c
                    self.step = 1
                    return LINES[0].replace("{name}", c["name"])
            return LINES[0].replace("{name}", "sir/madam")

        # Step 1: Ask for time to talk
        if self.step == 1:
            if "yes" in m:
                self.step = 2
                return LINES[1]
            else:
                return "May I know your relationship with the policyholder?"

        # Step 2: Show policy info with dynamic due_date
        if self.step == 2:
            c = self.customer
            self.step = 3
            return LINES[2].format(
                name=c["name"],
                policy_number=c.get("policynumber", "N/A"),
                purchase_date=c.get("purchasedate", "N/A"),
                due_date=c.get("duedate", "N/A"),
                premium=c.get("premium", "N/A"),
                product="Term Life"
            )

        # Step 3: Ask about reason for missing payment
        if self.step == 3:
            self.step = 4
            return LINES[3].format(due_date=self.customer.get("duedate", "N/A"))

        # Step 4: Ask if they know benefits
        if self.step == 4:
            self.step = 5
            return LINES[4]

        # Step 5: Offer solution
        if self.step == 5:
            self.step = 6
            return LINES[5]

        # Step 6: Ask about mode of payment
        if self.step == 6:
            if "online" in m or "cheque" in m or "cash" in m:
                self.step = 7
                return LINES[6]
            else:
                return LINES[5]

        # Step 7: Thank for confirming payment mode
        if self.step == 7:
            self.step = 8
            return LINES[7]

        # Step 8: Acknowledge payment if mentioned
        if any(k in m for k in ["paid", "last week", "i paid"]):
            self.step = 9
            return LINES[8]
        elif self.step == 8:
            self.step = 9
            return LINES[9]

        # Step 9: Ask about general queries
        if self.step >= 9:
            if any(w in m for w in ["term insurance", "what", "why", "benefit", "policy type"]):
                return ask_general(m)
            self.step = 99
            return LINES[-1]

        return "Could you please elaborate?"