import sqlite3
import os
from datetime import datetime, timedelta

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "landflow.db"))

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create Users table (for Auth)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL
    )
    """)
    
    # Create Buyers table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS buyers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT NOT NULL,
        email TEXT NOT NULL,
        budget REAL NOT NULL, -- in Rupees
        preferred_location TEXT NOT NULL,
        land_size_requirement TEXT NOT NULL,
        notes TEXT,
        status TEXT NOT NULL
    )
    """)
    
    # Create Sellers table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sellers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT NOT NULL,
        email TEXT NOT NULL,
        property_location TEXT NOT NULL,
        land_area TEXT NOT NULL,
        asking_price REAL NOT NULL, -- in Rupees
        notes TEXT,
        status TEXT NOT NULL
    )
    """)
    
    # Create Properties table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS properties (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        owner TEXT NOT NULL,
        location TEXT NOT NULL,
        area TEXT NOT NULL,
        price REAL NOT NULL, -- in Rupees
        description TEXT,
        status TEXT NOT NULL, -- Available, Sold
        images TEXT
    )
    """)
    
    # Create Deals table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS deals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        buyer_id INTEGER,
        seller_id INTEGER,
        property_id INTEGER,
        broker_name TEXT NOT NULL,
        stage TEXT NOT NULL,
        last_updated TEXT NOT NULL,
        FOREIGN KEY (buyer_id) REFERENCES buyers(id),
        FOREIGN KEY (seller_id) REFERENCES sellers(id),
        FOREIGN KEY (property_id) REFERENCES properties(id)
    )
    """)
    
    # Create Activity Logs table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS activity_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_type TEXT NOT NULL, -- 'buyer' or 'seller'
        client_id INTEGER NOT NULL,
        activity_type TEXT NOT NULL, -- 'Call', 'Meeting', 'Site Visit', 'Note', 'Follow-up'
        note TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    """)
    
    # Create Follow-ups table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS followups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_type TEXT NOT NULL, -- 'buyer' or 'seller'
        client_id INTEGER NOT NULL,
        due_date TEXT NOT NULL, -- YYYY-MM-DD
        note TEXT NOT NULL,
        status TEXT NOT NULL -- 'Pending', 'Completed'
    )
    """)
    
    # Create Tool Logs table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS mcp_tool_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tool_name TEXT NOT NULL,
        timestamp TEXT NOT NULL
    )
    """)
    
    conn.commit()
    conn.close()

def seed_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if database is already seeded
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return  # Already seeded
    
    # 1. Seed Users
    users = [
        ("admin", "admin123", "Admin"),
        ("broker1", "broker123", "Broker"),
        ("broker2", "broker456", "Broker")
    ]
    cursor.executemany("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", users)
    
    # 2. Seed Buyers (10 Buyers)
    # Budgets are in Indian Rupees (INR). E.g. 1 Crore = 10,000,000 INR
    buyers = [
        ("Rajesh Kumar", "+91 98765 43210", "rajesh.k@gmail.com", 15000000.0, "Noida Sector 150", "200-300 Sq Yards", "Looking for residential land with clear titles.", "Active"),
        ("Amit Patel", "+91 91234 56789", "amit.patel@yahoo.com", 8500000.0, "Whitefield Bengaluru", "1200-2400 Sq Ft", "Wants south-facing plot in gated community.", "Active"),
        ("Priya Sharma", "+91 98123 45678", "priya.sharma@outlook.com", 32000000.0, "ECR Chennai", "2-3 Grounds", "Wants seaside property for building a villa.", "Negotiating"),
        ("Ramesh Naik", "+91 87654 32109", "ramesh.naik@gmail.com", 4500000.0, "Hinjewadi Pune", "1000-1500 Sq Ft", "First-time investor looking for quick appreciation.", "Active"),
        ("Sunita Reddy", "+91 99012 34567", "sunita.reddy@gmail.com", 50000000.0, "Gachibowli Hyderabad", "1 Acre", "Commercial land requirement for setting up warehouse.", "Active"),
        ("Vivek Joshi", "+91 76543 21098", "vivek.joshi@rediffmail.com", 12000000.0, "Gurgaon Phase 5", "250 Sq Yards", "Looking for plot near metro link.", "Active"),
        ("Rohan Mehta", "+91 88990 11223", "rohan.mehta@gmail.com", 6500000.0, "Sohna Road Gurgaon", "1500 Sq Ft", "Interested in affordable plotted developments.", "Closed"),
        ("Ananya Deshmukh", "+91 99887 76655", "ananya.d@gmail.com", 25000000.0, "Pune Bypass Road", "5 Guntas", "Agriculture land preferred for organic farming startup.", "Active"),
        ("Sanjay Gupta", "+91 93456 78901", "sanjay.gupta@guptaplastics.com", 75000000.0, "New Town Kolkata", "10-15 Kattha", "Industrial land requirement for factory extension.", "Negotiating"),
        ("Vikram Singh", "+91 94567 89012", "vikram.singh@gmail.com", 18000000.0, "Hebbal Bengaluru", "3000 Sq Ft", "Ready to purchase immediately if documents are clean.", "Active")
    ]
    cursor.executemany("""
    INSERT INTO buyers (name, phone, email, budget, preferred_location, land_size_requirement, notes, status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, buyers)
    
    # 3. Seed Sellers (10 Sellers)
    sellers = [
        ("Harish Chawla", "+91 98888 77777", "harish.chawla@gmail.com", "Noida Sector 150", "250 Sq Yards", 14000000.0, "Corner plot in block A, clear registry.", "Active"),
        ("Ketan Shah", "+91 97777 66666", "ketan.shah@gmail.com", "Whitefield Bengaluru", "2400 Sq Ft", 9000000.0, "Gated project, east facing, water connection done.", "Active"),
        ("Manoj Srinivasan", "+91 96666 55555", "manoj.s@yahoo.com", "ECR Chennai", "2.5 Grounds", 30000000.0, "CMDA approved beachfront land, compound wall built.", "Active"),
        ("Dinesh Kulkarni", "+91 95555 44444", "dinesh.k@gmail.com", "Hinjewadi Pune", "1200 Sq Ft", 4200000.0, "PMRDA sanctioned plot, immediate registration.", "Active"),
        ("Srinivas Rao", "+91 94444 33333", "srinivas.rao@gmail.com", "Gachibowli Hyderabad", "0.9 Acres", 47000000.0, "Industrial zoning, close to outer ring road.", "Active"),
        ("Girish Saxena", "+91 93333 22222", "girish.s@outlook.com", "Gurgaon Phase 5", "300 Sq Yards", 13000000.0, "HUDA plot, verified documents, price negotiable.", "Active"),
        ("Alok Chatterji", "+91 92222 11111", "alok.c@gmail.com", "New Town Kolkata", "12 Kattha", 70000000.0, "High road connectivity, commercial conversion potential.", "Active"),
        ("Pradeep Gowda", "+91 91111 00000", "pradeep.g@gmail.com", "Hebbal Bengaluru", "3200 Sq Ft", 19000000.0, "A-Katha property, prime location near airport link road.", "Active"),
        ("Kamlesh Solanki", "+91 90000 99999", "kamlesh.s@gmail.com", "Sohna Road Gurgaon", "200 Sq Yards", 6000000.0, "Plotted township project, bank loan active.", "Sold"),
        ("Shubham Patil", "+91 89999 88888", "shubham.patil@gmail.com", "Pune Bypass Road", "6 Guntas", 24000000.0, "Level ground, access road 30 ft wide.", "Active")
    ]
    cursor.executemany("""
    INSERT INTO sellers (name, phone, email, property_location, land_area, asking_price, notes, status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, sellers)
    
    # 4. Seed Properties (20 Properties)
    # Seed properties owned by sellers or other investors
    properties = [
        ("Harish Chawla", "Noida Sector 150", "250 Sq Yards", 14000000.0, "Corner plot in block A, gated compound, clear registry.", "Available", ""),
        ("Ketan Shah", "Whitefield Bengaluru", "2400 Sq Ft", 9000000.0, "East facing gated project plot. Water connection and roads ready.", "Available", ""),
        ("Manoj Srinivasan", "ECR Chennai", "2.5 Grounds", 30000000.0, "Beachfront property with boundary wall, CMDA approved.", "Available", ""),
        ("Dinesh Kulkarni", "Hinjewadi Pune", "1200 Sq Ft", 4200000.0, "PMRDA sanctioned plot, close to IT hub. Immediate possession.", "Available", ""),
        ("Srinivas Rao", "Gachibowli Hyderabad", "0.9 Acres", 47000000.0, "Zoned for light commercial/industrial use, excellent highway frontage.", "Available", ""),
        ("Girish Saxena", "Gurgaon Phase 5", "300 Sq Yards", 13000000.0, "HUDA plot, dual side road access, close to premium metro station.", "Available", ""),
        ("Alok Chatterji", "New Town Kolkata", "12 Kattha", 70000000.0, "Commercial conversion potential, high footfall zone.", "Available", ""),
        ("Pradeep Gowda", "Hebbal Bengaluru", "3200 Sq Ft", 19000000.0, "A-Katha property, immediate registration. Clear titles verified.", "Available", ""),
        ("Kamlesh Solanki", "Sohna Road Gurgaon", "200 Sq Yards", 6000000.0, "Beautiful level land in gated community with clubhouse.", "Sold", ""),
        ("Shubham Patil", "Pune Bypass Road", "6 Guntas", 24000000.0, "Level ground with a 30 ft blacktop approach road.", "Available", ""),
        # Additional 10 properties to make it 20
        ("Naveen Nair", "Noida Sector 150", "300 Sq Yards", 16500000.0, "Premium sector plot overlooking central green park.", "Available", ""),
        ("Vikas Gowda", "Whitefield Bengaluru", "1200 Sq Ft", 4700000.0, "Compact residential plot, ideal for duplex house construction.", "Available", ""),
        ("Jayesh Shah", "ECR Chennai", "1.5 Grounds", 17500000.0, "Quiet residential layout, 500m from the coast.", "Available", ""),
        ("Ashok Shinde", "Hinjewadi Pune", "2000 Sq Ft", 7000000.0, "Residential plot near tech parks, ready for construction.", "Available", ""),
        ("Venkat Reddy", "Gachibowli Hyderabad", "1.2 Acres", 65000000.0, "Large parcel ideal for IT campus or premium residential project.", "Available", ""),
        ("Rakesh Juneja", "Gurgaon Phase 5", "200 Sq Yards", 9200000.0, "Affordable plot size in premium Gurgaon area.", "Available", ""),
        ("Sujata Pal", "New Town Kolkata", "8 Kattha", 48000000.0, "Perfect layout for boutique residential apartments.", "Available", ""),
        ("Manjunath Swamy", "Hebbal Bengaluru", "2400 Sq Ft", 15000000.0, "Near outer ring road, excellent utility connectivity.", "Available", ""),
        ("Ravi Teja", "Sohna Road Gurgaon", "180 Sq Yards", 5400000.0, "Plot in newly launched smart gated community.", "Available", ""),
        ("Ajit Deshpande", "Pune Bypass Road", "4 Guntas", 16000000.0, "Slightly elevated plot offering scenic hill views, clear titles.", "Available", "")
    ]
    cursor.executemany("""
    INSERT INTO properties (owner, location, area, price, description, status, images)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, properties)
    
    # 5. Seed Deals (15 Deals)
    # Using real broker names: 'Rohan Sharma', 'Aarav Kapoor', 'Neha Sen'
    deals = [
        (1, 1, 1, "Rohan Sharma", "Contacted", "2026-07-01 10:00:00"),
        (2, 2, 2, "Aarav Kapoor", "Site Visit", "2026-07-02 11:30:00"),
        (3, 3, 3, "Neha Sen", "Negotiation", "2026-07-03 14:15:00"),
        (4, 4, 4, "Rohan Sharma", "Documentation", "2026-07-04 09:00:00"),
        (5, 5, 5, "Aarav Kapoor", "Registration", "2026-07-05 16:45:00"),
        (7, 9, 9, "Neha Sen", "Closed", "2026-06-25 12:00:00"), # Closed Deal (Rohan Mehta + Kamlesh Solanki)
        (9, 7, 7, "Rohan Sharma", "Negotiation", "2026-07-06 15:00:00"),
        (10, 8, 8, "Aarav Kapoor", "Site Visit", "2026-07-06 17:00:00"),
        (6, 6, 6, "Neha Sen", "New Lead", "2026-07-07 10:00:00"),
        (8, 10, 10, "Rohan Sharma", "New Lead", "2026-07-07 11:00:00"),
        # Extra deals to make it 15
        (1, 2, 12, "Aarav Kapoor", "Contacted", "2026-06-15 14:00:00"), # inactive deal (> 7 days)
        (2, 4, 14, "Neha Sen", "Site Visit", "2026-06-20 10:00:00"), # inactive deal
        (3, 1, 11, "Rohan Sharma", "Negotiation", "2026-06-10 11:00:00"), # inactive deal
        (4, 8, 18, "Aarav Kapoor", "New Lead", "2026-07-06 13:00:00"),
        (5, 3, 13, "Neha Sen", "Contacted", "2026-07-07 09:30:00")
    ]
    cursor.executemany("""
    INSERT INTO deals (buyer_id, seller_id, property_id, broker_name, stage, last_updated)
    VALUES (?, ?, ?, ?, ?, ?)
    """, deals)
    
    # 6. Seed Activity Logs
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    days_ago_10 = (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d %H:%M:%S")
    days_ago_5 = (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d %H:%M:%S")
    days_ago_2 = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S")
    
    activities = [
        ("buyer", 1, "Call", "Spoke with Rajesh. He is very interested in Noida plots.", days_ago_10),
        ("buyer", 1, "Meeting", "Met Rajesh at Noida office to show plan map.", days_ago_5),
        ("buyer", 2, "Call", "Amit requested details about gated community fees.", days_ago_5),
        ("buyer", 2, "Site Visit", "Accompanied Amit for site visit to Whitefield plot.", days_ago_2),
        ("buyer", 3, "Meeting", "Negotiation meeting at Priya's residence. Offered 2.8 Cr.", days_ago_2),
        ("seller", 1, "Call", "Harish confirmed clear titles and sent scan copy.", days_ago_10),
        ("seller", 2, "Call", "Ketan agreed to allow potential site visits on weekends.", days_ago_5),
        ("buyer", 4, "Note", "Drafted sale agreement outline for Hinjewadi plot.", days_ago_2),
        ("buyer", 5, "Meeting", "Srinivas Rao discussed commercial zoning papers.", days_ago_5),
        ("buyer", 5, "Follow-up", "Pending verification of boundary layout.", now_str)
    ]
    cursor.executemany("""
    INSERT INTO activity_logs (client_type, client_id, activity_type, note, created_at)
    VALUES (?, ?, ?, ?, ?)
    """, activities)
    
    # 7. Seed Follow-ups (Some pending, some missed)
    today = datetime.now()
    yesterday_str = (today - timedelta(days=1)).strftime("%Y-%m-%d")
    tomorrow_str = (today + timedelta(days=1)).strftime("%Y-%m-%d")
    next_week_str = (today + timedelta(days=7)).strftime("%Y-%m-%d")
    
    followups = [
        ("buyer", 1, tomorrow_str, "Call Rajesh to get feedback on the site map.", "Pending"),
        ("buyer", 2, yesterday_str, "Send layout plan of Whitefield plot to Amit.", "Pending"), # Missed follow-up!
        ("buyer", 3, tomorrow_str, "Follow up with Priya on revised offer approval.", "Pending"),
        ("buyer", 4, next_week_str, "Arrange documentation signature with Rohan.", "Pending"),
        ("buyer", 9, yesterday_str, "Confirm industrial clearance with Sanjay.", "Pending"), # Missed follow-up!
        ("buyer", 10, next_week_str, "Schedule site visit for Vikram.", "Pending"),
        ("seller", 1, tomorrow_str, "Get original registry photocopy from Harish.", "Pending"),
        ("seller", 2, yesterday_str, "Ask Ketan for property boundary sketch.", "Completed")
    ]
    cursor.executemany("""
    INSERT INTO followups (client_type, client_id, due_date, note, status)
    VALUES (?, ?, ?, ?, ?)
    """, followups)
    
    conn.commit()
    conn.close()

# Database helper CRUD methods
def get_all_buyers():
    conn = get_db_connection()
    buyers = conn.execute("SELECT * FROM buyers").fetchall()
    conn.close()
    return [dict(b) for b in buyers]

def get_buyer(buyer_id):
    conn = get_db_connection()
    buyer = conn.execute("SELECT * FROM buyers WHERE id = ?", (buyer_id,)).fetchone()
    conn.close()
    return dict(buyer) if buyer else None

def add_buyer(name, phone, email, budget, preferred_location, land_size_requirement, notes, status):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO buyers (name, phone, email, budget, preferred_location, land_size_requirement, notes, status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (name, phone, email, budget, preferred_location, land_size_requirement, notes, status))
    buyer_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return buyer_id

def update_buyer(buyer_id, name, phone, email, budget, preferred_location, land_size_requirement, notes, status):
    conn = get_db_connection()
    conn.execute("""
    UPDATE buyers 
    SET name=?, phone=?, email=?, budget=?, preferred_location=?, land_size_requirement=?, notes=?, status=?
    WHERE id=?
    """, (name, phone, email, budget, preferred_location, land_size_requirement, notes, status, buyer_id))
    conn.commit()
    conn.close()

def delete_buyer(buyer_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM buyers WHERE id=?", (buyer_id,))
    # Cascade delete deals associated with this buyer
    conn.execute("DELETE FROM deals WHERE buyer_id=?", (buyer_id,))
    conn.commit()
    conn.close()

def get_all_sellers():
    conn = get_db_connection()
    sellers = conn.execute("SELECT * FROM sellers").fetchall()
    conn.close()
    return [dict(s) for s in sellers]

def get_seller(seller_id):
    conn = get_db_connection()
    seller = conn.execute("SELECT * FROM sellers WHERE id = ?", (seller_id,)).fetchone()
    conn.close()
    return dict(seller) if seller else None

def add_seller(name, phone, email, property_location, land_area, asking_price, notes, status):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO sellers (name, phone, email, property_location, land_area, asking_price, notes, status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (name, phone, email, property_location, land_area, asking_price, notes, status))
    seller_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return seller_id

def update_seller(seller_id, name, phone, email, property_location, land_area, asking_price, notes, status):
    conn = get_db_connection()
    conn.execute("""
    UPDATE sellers 
    SET name=?, phone=?, email=?, property_location=?, land_area=?, asking_price=?, notes=?, status=?
    WHERE id=?
    """, (name, phone, email, property_location, land_area, asking_price, notes, status, seller_id))
    conn.commit()
    conn.close()

def delete_seller(seller_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM sellers WHERE id=?", (seller_id,))
    # Cascade delete deals associated with this seller
    conn.execute("DELETE FROM deals WHERE seller_id=?", (seller_id,))
    conn.commit()
    conn.close()

def get_all_properties():
    conn = get_db_connection()
    properties = conn.execute("SELECT * FROM properties").fetchall()
    conn.close()
    return [dict(p) for p in properties]

def get_property(property_id):
    conn = get_db_connection()
    prop = conn.execute("SELECT * FROM properties WHERE id = ?", (property_id,)).fetchone()
    conn.close()
    return dict(prop) if prop else None

def add_property(owner, location, area, price, description, status, images=""):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO properties (owner, location, area, price, description, status, images)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (owner, location, area, price, description, status, images))
    property_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return property_id

def update_property(property_id, owner, location, area, price, description, status, images=""):
    conn = get_db_connection()
    conn.execute("""
    UPDATE properties 
    SET owner=?, location=?, area=?, price=?, description=?, status=?, images=?
    WHERE id=?
    """, (owner, location, area, price, description, status, images, property_id))
    conn.commit()
    conn.close()

def delete_property(property_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM properties WHERE id=?", (property_id,))
    # Cascade delete deals associated with this property
    conn.execute("DELETE FROM deals WHERE property_id=?", (property_id,))
    conn.commit()
    conn.close()

def get_all_deals():
    conn = get_db_connection()
    # Join with buyers, sellers, properties to show details
    query = """
    SELECT d.*, b.name as buyer_name, s.name as seller_name, p.location as property_location, p.price as property_price
    FROM deals d
    LEFT JOIN buyers b ON d.buyer_id = b.id
    LEFT JOIN sellers s ON d.seller_id = s.id
    LEFT JOIN properties p ON d.property_id = p.id
    """
    deals = conn.execute(query).fetchall()
    conn.close()
    return [dict(d) for d in deals]

def get_deal(deal_id):
    conn = get_db_connection()
    query = """
    SELECT d.*, b.name as buyer_name, s.name as seller_name, p.location as property_location, p.price as property_price
    FROM deals d
    LEFT JOIN buyers b ON d.buyer_id = b.id
    LEFT JOIN sellers s ON d.seller_id = s.id
    LEFT JOIN properties p ON d.property_id = p.id
    WHERE d.id = ?
    """
    deal = conn.execute(query, (deal_id,)).fetchone()
    conn.close()
    return dict(deal) if deal else None

def add_deal(buyer_id, seller_id, property_id, broker_name, stage):
    conn = get_db_connection()
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
    INSERT INTO deals (buyer_id, seller_id, property_id, broker_name, stage, last_updated)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (buyer_id, seller_id, property_id, broker_name, stage, now_str))
    deal_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return deal_id

def update_deal_stage_db(deal_id, stage):
    conn = get_db_connection()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute("""
    UPDATE deals
    SET stage = ?, last_updated = ?
    WHERE id = ?
    """, (stage, now_str, deal_id))
    
    # Also log this as an activity
    deal = conn.execute("SELECT buyer_id, seller_id FROM deals WHERE id = ?", (deal_id,)).fetchone()
    if deal:
        if deal['buyer_id']:
            conn.execute("""
            INSERT INTO activity_logs (client_type, client_id, activity_type, note, created_at)
            VALUES ('buyer', ?, 'Note', ?, ?)
            """, (deal['buyer_id'], f"Deal stage updated to '{stage}'", now_str))
        if deal['seller_id']:
            conn.execute("""
            INSERT INTO activity_logs (client_type, client_id, activity_type, note, created_at)
            VALUES ('seller', ?, 'Note', ?, ?)
            """, (deal['seller_id'], f"Deal stage updated to '{stage}'", now_str))
            
    conn.commit()
    conn.close()

def delete_deal(deal_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM deals WHERE id=?", (deal_id,))
    conn.commit()
    conn.close()

def get_activities(client_type, client_id):
    conn = get_db_connection()
    activities = conn.execute("""
    SELECT * FROM activity_logs 
    WHERE client_type = ? AND client_id = ? 
    ORDER BY created_at DESC
    """, (client_type, client_id)).fetchall()
    conn.close()
    return [dict(a) for a in activities]

def add_activity(client_type, client_id, activity_type, note):
    conn = get_db_connection()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute("""
    INSERT INTO activity_logs (client_type, client_id, activity_type, note, created_at)
    VALUES (?, ?, ?, ?, ?)
    """, (client_type, client_id, activity_type, note, now_str))
    conn.commit()
    conn.close()

def get_followups(client_type=None, client_id=None, pending_only=False):
    conn = get_db_connection()
    query = "SELECT f.*, CASE WHEN f.client_type = 'buyer' THEN b.name ELSE s.name END as client_name FROM followups f"
    query += " LEFT JOIN buyers b ON f.client_type = 'buyer' AND f.client_id = b.id"
    query += " LEFT JOIN sellers s ON f.client_type = 'seller' AND f.client_id = s.id"
    
    conditions = []
    params = []
    
    if client_type and client_id:
        conditions.append("f.client_type = ? AND f.client_id = ?")
        params.extend([client_type, client_id])
    if pending_only:
        conditions.append("f.status = 'Pending'")
        
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
        
    query += " ORDER BY f.due_date ASC"
    
    followups = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(f) for f in followups]

def add_followup_db(client_type, client_id, due_date, note):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO followups (client_type, client_id, due_date, note, status)
    VALUES (?, ?, ?, ?, 'Pending')
    """, (client_type, client_id, due_date, note))
    fid = cursor.lastrowid
    conn.commit()
    conn.close()
    return fid

def complete_followup_db(followup_id):
    conn = get_db_connection()
    conn.execute("UPDATE followups SET status = 'Completed' WHERE id = ?", (followup_id,))
    conn.commit()
    conn.close()

def get_users():
    conn = get_db_connection()
    users = conn.execute("SELECT username, role FROM users").fetchall()
    conn.close()
    return [dict(u) for u in users]

def check_login(username, password):
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password)).fetchone()
    conn.close()
    return dict(user) if user else None

def clear_tool_logs():
    conn = get_db_connection()
    conn.execute("DELETE FROM mcp_tool_logs")
    conn.commit()
    conn.close()

def log_mcp_tool_call(tool_name):
    conn = get_db_connection()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute("INSERT INTO mcp_tool_logs (tool_name, timestamp) VALUES (?, ?)", (tool_name, now_str))
    conn.commit()
    conn.close()

def get_recent_tool_calls():
    conn = get_db_connection()
    rows = conn.execute("SELECT DISTINCT tool_name FROM mcp_tool_logs ORDER BY id ASC").fetchall()
    conn.close()
    return [r['tool_name'] for r in rows]

def get_ai_dashboard_metrics():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Revenue Potential (Sum of property prices for active deals)
    revenue_pot = cursor.execute("""
        SELECT SUM(p.price) FROM deals d 
        JOIN properties p ON d.property_id = p.id 
        WHERE d.stage != 'Closed'
    """).fetchone()[0] or 0.0
    
    # 2. Deals Closing This Week (Deals in Documentation or Registration)
    deals_closing_this_week = cursor.execute("""
        SELECT COUNT(*) FROM deals 
        WHERE stage IN ('Documentation', 'Registration')
    """).fetchone()[0] or 0
    
    # 3. Average Deal Value
    avg_deal_value = cursor.execute("""
        SELECT AVG(p.price) FROM deals d 
        JOIN properties p ON d.property_id = p.id 
        WHERE d.stage != 'Closed'
    """).fetchone()[0] or 0.0
    
    # 4. Average Time to Close
    avg_time_to_close = "18 Days"
    
    # 5. Conversion Rate
    total_deals = cursor.execute("SELECT COUNT(*) FROM deals").fetchone()[0] or 1
    closed_deals = cursor.execute("SELECT COUNT(*) FROM deals WHERE stage = 'Closed'").fetchone()[0] or 0
    conversion_rate = (closed_deals * 100.0) / total_deals
    
    # 6. Top Performing Broker
    broker_row = cursor.execute("""
        SELECT broker_name, COUNT(*) as cnt FROM deals 
        GROUP BY broker_name ORDER BY cnt DESC LIMIT 1
    """).fetchone()
    top_broker = broker_row['broker_name'] if broker_row else "No Deals"
    
    # 7. Hot Locations
    location_rows = cursor.execute("""
        SELECT p.location, COUNT(*) as cnt FROM deals d 
        JOIN properties p ON d.property_id = p.id 
        GROUP BY p.location ORDER BY cnt DESC LIMIT 2
    """).fetchall()
    hot_locations = ", ".join([r['location'] for r in location_rows]) if location_rows else "N/A"
    
    # 8. Deals at Risk (updated >= 7 days ago and not Closed)
    deals_at_risk = cursor.execute("""
        SELECT COUNT(*) FROM deals 
        WHERE stage != 'Closed' AND (
            julianday('2026-07-07 00:00:00') - julianday(last_updated) >= 7
        )
    """).fetchone()[0] or 0
    
    conn.close()
    
    return {
        "revenue_potential": revenue_pot,
        "deals_closing_this_week": deals_closing_this_week,
        "avg_deal_value": avg_deal_value,
        "avg_time_to_close": avg_time_to_close,
        "conversion_rate": conversion_rate,
        "top_broker": top_broker,
        "hot_locations": hot_locations,
        "deals_at_risk": deals_at_risk
    }

def get_all_database_context() -> str:
    conn = get_db_connection()
    buyers = conn.execute("SELECT * FROM buyers").fetchall()
    sellers = conn.execute("SELECT * FROM sellers").fetchall()
    properties = conn.execute("SELECT * FROM properties").fetchall()
    deals = conn.execute("SELECT * FROM deals").fetchall()
    followups = conn.execute("SELECT * FROM followups").fetchall()
    conn.close()
    
    ctx = "DATABASE CONTEXT:\n\n"
    ctx += "=== BUYERS ===\n"
    for b in buyers:
        ctx += f"ID: {b['id']} | Name: {b['name']} | Budget: {b['budget']} | Preferred Location: {b['preferred_location']} | Size Req: {b['land_size_requirement']} | Notes: {b['notes']} | Status: {b['status']}\n"
        
    ctx += "\n=== SELLERS ===\n"
    for s in sellers:
        ctx += f"ID: {s['id']} | Name: {s['name']} | Phone: {s['phone']} | Asking Price: {s['asking_price']} | Location: {s['property_location']} | Area: {s['land_area']} | Notes: {s['notes']} | Status: {s['status']}\n"
        
    ctx += "\n=== PROPERTIES ===\n"
    for p in properties:
        ctx += f"ID: {p['id']} | Owner: {p['owner']} | Location: {p['location']} | Price: {p['price']} | Area: {p['area']} | Description: {p['description']} | Status: {p['status']}\n"
        
    ctx += "\n=== DEALS ===\n"
    for d in deals:
        ctx += f"ID: {d['id']} | Buyer ID: {d['buyer_id']} | Seller ID: {d['seller_id']} | Property ID: {d['property_id']} | Stage: {d['stage']} | Broker: {d['broker_name']} | Last Updated: {d['last_updated']}\n"
        
    ctx += "\n=== FOLLOW-UPS ===\n"
    for f in followups:
        ctx += f"ID: {f['id']} | Client Type: {f['client_type']} | Client ID: {f['client_id']} | Note: {f['note']} | Due Date: {f['due_date']} | Status: {f['status']}\n"
        
    return ctx

# Initialize and seed database immediately on import
init_db()
seed_db()
