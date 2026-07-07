from mcp.server.fastmcp import FastMCP
import os
import sqlite3
from datetime import datetime, timedelta
import database

mcp = FastMCP("LandFlowMCP")

@mcp.tool()
def search_buyers(query: str) -> str:
    """Searches the buyer database for matching names, locations, notes, or statuses.
    
    Args:
        query: Search term (e.g., 'Rajesh', 'Noida', 'Active').
    """
    database.log_mcp_tool_call("search_buyers")
    conn = database.get_db_connection()
    q = f"%{query}%"
    rows = conn.execute("""
        SELECT * FROM buyers 
        WHERE name LIKE ? 
           OR preferred_location LIKE ? 
           OR notes LIKE ? 
           OR status LIKE ?
    """, (q, q, q, q)).fetchall()
    conn.close()
    
    if not rows:
        return f"No buyers found matching query: '{query}'"
        
    result = []
    for r in rows:
        d = dict(r)
        result.append(
            f"ID: {d['id']} | Name: {d['name']} | Phone: {d['phone']} | Email: {d['email']} | "
            f"Budget: ₹{d['budget']:,.2f} | Preferred Location: {d['preferred_location']} | "
            f"Land Size: {d['land_size_requirement']} | Notes: {d['notes']} | Status: {d['status']}"
        )
    return "\n".join(result)

@mcp.tool()
def search_sellers(query: str) -> str:
    """Searches the seller database for matching names, property locations, notes, or statuses.
    
    Args:
        query: Search term (e.g., 'Shah', 'Bengaluru', 'Active').
    """
    database.log_mcp_tool_call("search_sellers")
    conn = database.get_db_connection()
    q = f"%{query}%"
    rows = conn.execute("""
        SELECT * FROM sellers 
        WHERE name LIKE ? 
           OR property_location LIKE ? 
           OR notes LIKE ? 
           OR status LIKE ?
    """, (q, q, q, q)).fetchall()
    conn.close()
    
    if not rows:
        return f"No sellers found matching query: '{query}'"
        
    result = []
    for r in rows:
        d = dict(r)
        result.append(
            f"ID: {d['id']} | Name: {d['name']} | Phone: {d['phone']} | Email: {d['email']} | "
            f"Location: {d['property_location']} | Land Area: {d['land_area']} | "
            f"Asking Price: ₹{d['asking_price']:,.2f} | Notes: {d['notes']} | Status: {d['status']}"
        )
    return "\n".join(result)

@mcp.tool()
def search_properties(location: str = None, min_price: float = None, max_price: float = None, min_area_sqft: float = None) -> str:
    """Searches and filters the property database based on location, price range, and area.
    
    Args:
        location: Property location filter (case-insensitive substring, optional).
        min_price: Minimum price in Rupees (optional).
        max_price: Maximum price in Rupees (optional).
        min_area_sqft: Minimum area in sqft (optional, e.g. for parsing numbers from area descriptions).
    """
    database.log_mcp_tool_call("search_properties")
    conn = database.get_db_connection()
    query = "SELECT * FROM properties WHERE 1=1"
    params = []
    
    if location:
        query += " AND location LIKE ?"
        params.append(f"%{location}%")
    if min_price is not None:
        query += " AND price >= ?"
        params.append(min_price)
    if max_price is not None:
        query += " AND price <= ?"
        params.append(max_price)
        
    rows = conn.execute(query, params).fetchall()
    conn.close()
    
    if not rows:
        return "No properties found matching the filter criteria."
        
    result = []
    for r in rows:
        d = dict(r)
        # Check area filter if specified (crude check: if 'Sq Ft' or 'Sq Yards' matches)
        if min_area_sqft:
            area_str = d['area'].lower()
            val = 0.0
            # Try to extract the number
            import re
            m = re.search(r"(\d+(\.\d+)?)", area_str)
            if m:
                val = float(m.group(1))
            if 'yard' in area_str:
                val *= 9.0  # 1 Sq Yard = 9 Sq Ft approx
            if 'acre' in area_str:
                val *= 43560.0  # 1 Acre = 43,560 Sq Ft
            if 'gunto' in area_str or 'gunta' in area_str:
                val *= 1089.0  # 1 Gunta = 1089 Sq Ft approx
            if val < min_area_sqft:
                continue
                
        result.append(
            f"Property ID: {d['id']} | Owner: {d['owner']} | Location: {d['location']} | "
            f"Area: {d['area']} | Price: ₹{d['price']:,.2f} | Status: {d['status']} | "
            f"Description: {d['description']}"
        )
        
    if not result:
        return "No properties found matching the filter criteria after area filtering."
    return "\n".join(result)

@mcp.tool()
def update_deal_stage(deal_id: int, stage: str) -> str:
    """Updates the pipeline stage of a deal.
    
    Args:
        deal_id: The ID of the deal to update.
        stage: The new stage (New Lead, Contacted, Site Visit, Negotiation, Documentation, Registration, Closed).
    """
    database.log_mcp_tool_call("update_deal_stage")
    valid_stages = ["New Lead", "Contacted", "Site Visit", "Negotiation", "Documentation", "Registration", "Closed"]
    if stage not in valid_stages:
        return f"Invalid stage '{stage}'. Must be one of: {', '.join(valid_stages)}"
        
    conn = database.get_db_connection()
    deal = conn.execute("SELECT id FROM deals WHERE id = ?", (deal_id,)).fetchone()
    conn.close()
    
    if not deal:
        return f"Deal with ID {deal_id} not found."
        
    database.update_deal_stage_db(deal_id, stage)
    return f"Successfully updated Deal ID {deal_id} to stage '{stage}'."

@mcp.tool()
def add_followup(client_type: str, client_id: int, due_date: str, note: str) -> str:
    """Adds a pending follow-up task for a buyer or seller.
    
    Args:
        client_type: 'buyer' or 'seller'.
        client_id: The ID of the buyer or seller.
        due_date: The due date in YYYY-MM-DD format.
        note: Details of the follow-up.
    """
    database.log_mcp_tool_call("add_followup")
    if client_type not in ["buyer", "seller"]:
        return "Invalid client_type. Must be 'buyer' or 'seller'."
        
    conn = database.get_db_connection()
    if client_type == "buyer":
        exists = conn.execute("SELECT id FROM buyers WHERE id = ?", (client_id,)).fetchone()
    else:
        exists = conn.execute("SELECT id FROM sellers WHERE id = ?", (client_id,)).fetchone()
    conn.close()
    
    if not exists:
        return f"Client of type '{client_type}' with ID {client_id} not found."
        
    try:
        datetime.strptime(due_date, "%Y-%m-%d")
    except ValueError:
        return "Invalid date format. Must be YYYY-MM-DD."
        
    fid = database.add_followup_db(client_type, client_id, due_date, note)
    return f"Successfully scheduled follow-up (ID: {fid}) on {due_date} for {client_type} ID {client_id}."

@mcp.tool()
def get_dashboard_stats() -> str:
    """Retrieves high-level summary statistics of the entire LandFlow CRM database."""
    database.log_mcp_tool_call("get_dashboard_stats")
    conn = database.get_db_connection()
    
    # Counts
    buyers_cnt = conn.execute("SELECT COUNT(*) FROM buyers").fetchone()[0]
    sellers_cnt = conn.execute("SELECT COUNT(*) FROM sellers").fetchone()[0]
    properties_cnt = conn.execute("SELECT COUNT(*) FROM properties").fetchone()[0]
    deals_cnt = conn.execute("SELECT COUNT(*) FROM deals").fetchone()[0]
    active_deals = conn.execute("SELECT COUNT(*) FROM deals WHERE stage != 'Closed'").fetchone()[0]
    
    # Follow-ups (Pending & Overdue)
    today_str = datetime.now().strftime("%Y-%m-%d")
    pending_followups = conn.execute("SELECT COUNT(*) FROM followups WHERE status = 'Pending'").fetchone()[0]
    overdue_followups = conn.execute("SELECT COUNT(*) FROM followups WHERE status = 'Pending' AND due_date < ?", (today_str,)).fetchone()[0]
    
    # Deals per stage
    stages = conn.execute("SELECT stage, COUNT(*) FROM deals GROUP BY stage").fetchall()
    stages_str = ", ".join(f"{r[0]}: {r[1]}" for r in stages)
    
    # Average Asking Price
    avg_price = conn.execute("SELECT AVG(asking_price) FROM sellers").fetchone()[0] or 0.0
    
    conn.close()
    
    return (
        f"Total Buyers: {buyers_cnt}\n"
        f"Total Sellers: {sellers_cnt}\n"
        f"Total Properties: {properties_cnt}\n"
        f"Total Deals: {deals_cnt} (Active: {active_deals})\n"
        f"Deals by Stage: {stages_str}\n"
        f"Pending Follow-ups: {pending_followups} (Overdue: {overdue_followups})\n"
        f"Average Land Asking Price: ₹{avg_price:,.2f}"
    )

if __name__ == "__main__":
    mcp.run()
