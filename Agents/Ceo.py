from utils.deepseek import call_deepseek

def ceo_agent():
    system = """You are the CEO of Neo Vision Hub, an information blog. 
    You communicate with the owner in Roman Urdu.
    Your job is to create a daily task plan for the team."""
    
    user = "Aaj ke liye team ko kya plan dena chahiye? 3 points mein Roman Urdu mein batao."
    return call_deepseek(system, user, 500)
