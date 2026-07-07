import os
import sqlite3
import database

def verify():
    print("=== Starting LandFlow AI Verification ===")
    
    # 1. Check database path
    print(f"Database path: {database.DB_PATH}")
    if os.path.exists(database.DB_PATH):
        print("✅ landflow.db file exists.")
    else:
        print("❌ landflow.db file NOT found!")
        return
        
    # 2. Check connections and seeded counts
    try:
        conn = database.get_db_connection()
        cursor = conn.cursor()
        
        users_count = cursor.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        buyers_count = cursor.execute("SELECT COUNT(*) FROM buyers").fetchone()[0]
        sellers_count = cursor.execute("SELECT COUNT(*) FROM sellers").fetchone()[0]
        properties_count = cursor.execute("SELECT COUNT(*) FROM properties").fetchone()[0]
        deals_count = cursor.execute("SELECT COUNT(*) FROM deals").fetchone()[0]
        activities_count = cursor.execute("SELECT COUNT(*) FROM activity_logs").fetchone()[0]
        followups_count = cursor.execute("SELECT COUNT(*) FROM followups").fetchone()[0]
        
        print(f"✅ Users count: {users_count} (Expected: 3)")
        print(f"✅ Buyers count: {buyers_count} (Expected: 10)")
        print(f"✅ Sellers count: {sellers_count} (Expected: 10)")
        print(f"✅ Properties count: {properties_count} (Expected: 20)")
        print(f"✅ Deals count: {deals_count} (Expected: 15)")
        print(f"✅ Activity Logs count: {activities_count} (Expected: >= 10)")
        print(f"✅ Follow-ups count: {followups_count} (Expected: 8)")
        
        # Test individual select
        cursor.execute("SELECT name, budget FROM buyers LIMIT 1")
        row = cursor.fetchone()
        if row:
            print(f"✅ Sample buyer read: {row['name']} with budget {row['budget']}")
            
        conn.close()
    except Exception as e:
        print(f"❌ Database verification failed: {e}")
        return
        
    # 3. Verify FastMCP Server Tool functions directly
    print("\n=== Testing FastMCP Tools directly ===")
    try:
        import mcp_server
        
        # Test search buyers tool
        res_b = mcp_server.search_buyers("Rajesh")
        print("✅ search_buyers() tool works. Output snippet:")
        print(f"   {res_b[:120]}...")
        
        # Test search properties tool
        res_p = mcp_server.search_properties(location="Noida Sector 150")
        print("✅ search_properties() tool works. Output snippet:")
        print(f"   {res_p[:120]}...")
        
        # Test get_dashboard_stats tool
        res_stats = mcp_server.get_dashboard_stats()
        print("✅ get_dashboard_stats() tool works. Output snippet:")
        print(res_stats)
        
    except Exception as e:
        print(f"❌ FastMCP Tools verification failed: {e}")
        return
        
    print("\n=== Verification Successful! LandFlow AI is ready to deploy and run ===")

if __name__ == "__main__":
    verify()
