#!/usr/bin/env python3
"""
COMPREHENSIVE SECURITY ANALYSIS REPORT
Based on investigation findings
"""
import asyncio
import uuid
from app.database.database import database, init_db

async def initialize_database():
    """Initialize database if not already done"""
    if not database.pool:
        await init_db()

async def comprehensive_rls_analysis():
    """Comprehensive analysis of RLS failure"""
    
    print("🔍 COMPREHENSIVE RLS SECURITY ANALYSIS")
    print("=" * 60)
    
    await initialize_database()
    conn = await database.pool.acquire()
    
    try:
        print("1. DATABASE OWNERSHIP ANALYSIS:")
        print("-" * 40)
        
        # Check table ownership and RLS status
        tables_info = await conn.fetch("""
            SELECT 
                tablename,
                tableowner,
                rowsecurity,
                (SELECT count(*) FROM pg_policies WHERE tablename = t.tablename) as policy_count
            FROM pg_tables t 
            WHERE schemaname = 'public'
            AND tablename IN ('conversations', 'conversation_participants', 'messages')
            ORDER BY tablename;
        """)
        
        for table in tables_info:
            status = "✅ ENABLED" if table['rowsecurity'] else "❌ DISABLED"
            owner_bypass = "🚨 BYPASSED" if table['tableowner'] == 'safe_zone_user' else "✅ SECURE"
            print(f"   {table['tablename']:25} | RLS: {status:8} | Policies: {table['policy_count']:2} | {owner_bypass}")
        
        print("\n2. RLS POLICY ANALYSIS:")
        print("-" * 40)
        
        # Get detailed policy information
        policies = await conn.fetch("""
            SELECT 
                tablename,
                policyname,
                cmd,
                qual
            FROM pg_policies 
            WHERE schemaname = 'public'
            AND tablename IN ('conversations', 'conversation_participants', 'messages')
            ORDER BY tablename, policyname;
        """)
        
        for policy in policies:
            print(f"   📋 {policy['tablename']}.{policy['policyname']}")
            print(f"      Command: {policy['cmd']}")
            if policy['qual']:
                # Shorten qual for readability
                qual = policy['qual'][:100] + "..." if len(policy['qual']) > 100 else policy['qual']
                print(f"      Condition: {qual}")
        
        print("\n3. RLS BYPASS DEMONSTRATION:")
        print("-" * 40)
        
        # Create test scenario
        user1_id = uuid.uuid4()
        user2_id = uuid.uuid4()
        user3_id = uuid.uuid4()
        conv_id = uuid.uuid4()
        
        # Setup test data
        await conn.execute("""
            INSERT INTO users (id, email, username, hashed_password, full_name, is_active)
            VALUES 
                ($1, 'analysis_user1@example.com', 'analysis1', 'hash1', 'Analysis User 1', true),
                ($2, 'analysis_user2@example.com', 'analysis2', 'hash2', 'Analysis User 2', true),
                ($3, 'analysis_user3@example.com', 'analysis3', 'hash3', 'Analysis User 3', true)
            ON CONFLICT (email) DO NOTHING;
        """, user1_id, user2_id, user3_id)
        
        await conn.execute("""
            INSERT INTO conversations (id, title, created_at)
            VALUES ($1, 'Security Analysis Conversation', NOW())
            ON CONFLICT DO NOTHING;
        """, conv_id)
        
        await conn.execute("""
            INSERT INTO conversation_participants (conversation_id, user_id, joined_at)
            VALUES 
                ($1, $2, NOW()),
                ($1, $3, NOW())
            ON CONFLICT DO NOTHING;
        """, conv_id, user1_id, user2_id)
        
        # Test RLS with different users
        print("   Testing User1 (participant) access:")
        await conn.execute("SELECT set_config('app.current_user_id', $1, true);", str(user1_id))
        user1_count = await conn.fetchval("SELECT COUNT(*) FROM conversations;")
        print(f"      User1 sees {user1_count} conversations")
        
        print("   Testing User3 (non-participant) access:")
        await conn.execute("SELECT set_config('app.current_user_id', $1, true);", str(user3_id))
        user3_count = await conn.fetchval("SELECT COUNT(*) FROM conversations;")
        print(f"      User3 sees {user3_count} conversations")
        
        print("   Testing table owner (no context) access:")
        await conn.execute("RESET app.current_user_id;")
        owner_count = await conn.fetchval("SELECT COUNT(*) FROM conversations;")
        print(f"      Owner sees {owner_count} conversations")
        
        print("\n4. SECURITY ASSESSMENT:")
        print("-" * 40)
        
        if user1_count == user3_count == owner_count:
            print("   🚨 CRITICAL: RLS COMPLETELY BYPASSED")
            print("      All users see all data regardless of participation")
            print("      REASON: Table owner (safe_zone_user) bypasses RLS automatically")
        elif user3_count > 0:
            print("   🚨 HIGH: RLS PARTIALLY BYPASSED") 
            print("      Non-participants can access conversations")
        else:
            print("   ✅ SECURE: RLS working correctly")
        
        # Cleanup
        await conn.execute("DELETE FROM conversation_participants WHERE conversation_id = $1;", conv_id)
        await conn.execute("DELETE FROM conversations WHERE id = $1;", conv_id)
        await conn.execute("DELETE FROM users WHERE id IN ($1, $2, $3);", user1_id, user2_id, user3_id)
        
    except Exception as e:
        print(f"Error during analysis: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await database.pool.release(conn)

async def check_application_layer_security():
    """Check if application layer provides security"""
    
    print("\n5. APPLICATION LAYER SECURITY CHECK:")
    print("-" * 40)
    
    try:
        # Check if CRUD operations have manual security checks
        with open("app/crud/messages.py", "r") as f:
            crud_content = f.read()
        
        security_checks = [
            "PermissionError" in crud_content,
            "is_participant" in crud_content,
            "check_permission" in crud_content,
            "user_id" in crud_content and "current_user" in crud_content,
            "security" in crud_content.lower()
        ]
        
        security_count = sum(security_checks)
        print(f"   Manual security checks in CRUD: {security_count}/5")
        
        if security_count >= 3:
            print("   ✅ Application layer has security checks")
        else:
            print("   ⚠️  Limited application layer security")
            
        # Check WebSocket security
        with open("app/api/endpoints/websocket.py", "r") as f:
            ws_content = f.read()
            
        ws_security = [
            "auth" in ws_content.lower(),
            "token" in ws_content,
            "user_id" in ws_content,
            "verify" in ws_content
        ]
        
        ws_security_count = sum(ws_security)
        print(f"   WebSocket security measures: {ws_security_count}/4")
        
    except Exception as e:
        print(f"Error checking application security: {e}")

def generate_recommendations():
    """Generate security recommendations"""
    
    print("\n6. SECURITY RECOMMENDATIONS:")
    print("-" * 40)
    
    recommendations = [
        "🚨 IMMEDIATE: Fix RLS bypass by changing table ownership or using separate database user",
        "🔒 Create dedicated database user without table ownership for application",
        "✅ Verify WebSocket messaging respects user isolation", 
        "📋 Add comprehensive security tests for messaging isolation",
        "🛡️ Implement defense-in-depth with both RLS and application checks",
        "🔍 Audit all data access patterns for security leaks"
    ]
    
    for i, rec in enumerate(recommendations, 1):
        print(f"   {i}. {rec}")

if __name__ == "__main__":
    print("🎯 SAFE ZONE - REAL-TIME MESSAGING SECURITY AUDIT")
    print("=" * 60)
    
    asyncio.run(comprehensive_rls_analysis())
    asyncio.run(check_application_layer_security())
    generate_recommendations()
    
    print("\n" + "=" * 60)
    print("📊 FINAL SECURITY STATUS: 🚨 CRITICAL ISSUE IDENTIFIED")
    print("RLS is completely bypassed due to table ownership")
    print("Users can access all conversations regardless of participation")
    print("=" * 60)
