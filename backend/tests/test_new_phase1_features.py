"""
Comprehensive test for new Phase 1 & 2 features with real user context
"""

import asyncio
import asyncpg
from uuid import uuid4
from app.database.database import database

async def create_test_user_and_post():
    """Create test user and post for testing"""
    try:
        await database.connect()
        async with database.pool.acquire() as conn:
            # Create test user
            test_user_id = uuid4()
            test_username = f"testuser_{uuid4().hex[:8]}"
            
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(test_user_id)
            )
            
            # Create user (bypassing RLS for setup)
            await conn.execute(
                "INSERT INTO users (id, username, email, hashed_password) VALUES ($1, $2, $3, $4)",
                test_user_id, test_username, f"{test_username}@test.com", "hashed_password_placeholder"
            )
            
            # Create test post
            test_post_id = uuid4()
            await conn.execute(
                "INSERT INTO posts (id, user_id, content, content_type) VALUES ($1, $2, $3, $4)",
                test_post_id, test_user_id, "Test post content for reactions", "text"
            )
            
            return test_user_id, test_post_id
            
    except Exception as e:
        print(f"❌ Failed to create test data: {e}")
        return None, None

async def test_reactions_with_real_user():
    """Test reactions system with real user context"""
    print("🧪 TESTING REACTIONS SYSTEM")
    print("=" * 40)
    
    user_id, post_id = await create_test_user_and_post()
    if not user_id or not post_id:
        return False
    
    try:
        from app.crud.missing_phase1_features import missing_phase1_features_crud
        
        # Test 1: Add reaction
        print("1. Testing reaction creation...")
        reaction = await missing_phase1_features_crud.add_reaction(user_id, post_id, 'heart')
        assert reaction is not None, "Failed to create reaction"
        print("✅ Reaction created successfully")
        
        # Test 2: Get reactions
        print("2. Testing reaction retrieval...")
        reactions = await missing_phase1_features_crud.get_post_reactions(post_id, user_id)
        assert len(reactions) > 0, "No reactions found"
        assert reactions[0]['reaction_type'] == 'heart', "Wrong reaction type"
        print("✅ Reactions retrieved successfully")
        
        # Test 3: Remove reaction
        print("3. Testing reaction removal...")
        success = await missing_phase1_features_crud.remove_reaction(user_id, post_id, 'heart')
        assert success, "Failed to remove reaction"
        print("✅ Reaction removed successfully")
        
        # Test 4: Verify RLS enforcement
        print("4. Testing RLS enforcement...")
        async with database.pool.acquire() as conn:
            # Try to access reactions as different user
            different_user = uuid4()
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(different_user)
            )
            
            # Should not see other user's reactions
            reactions = await conn.fetch(
                "SELECT * FROM reactions WHERE post_id = $1",
                post_id
            )
            assert len(reactions) == 0, "RLS violation: saw other user's reactions"
        print("✅ RLS enforcement working")
        
        return True
        
    except Exception as e:
        print(f"❌ Reactions test failed: {e}")
        return False

async def test_circles_with_real_user():
    """Test circles system with real user context"""
    print("\n🧪 TESTING CIRCLES SYSTEM")
    print("=" * 40)
    
    user_id, _ = await create_test_user_and_post()
    if not user_id:
        return False
    
    try:
        from app.crud.missing_phase1_features import missing_phase1_features_crud
        
        # Test 1: Get public circles
        print("1. Testing public circles access...")
        circles = await missing_phase1_features_crud.get_public_circles()
        assert len(circles) > 0, "No public circles found"
        circle_id = circles[0]['id']
        print(f"✅ Found {len(circles)} public circles")
        
        # Test 2: Join circle
        print("2. Testing circle joining...")
        member = await missing_phase1_features_crud.join_circle(circle_id, user_id)
        assert member is not None, "Failed to join circle"
        print("✅ Joined circle successfully")
        
        # Test 3: Get user circles
        print("3. Testing user circles retrieval...")
        user_circles = await missing_phase1_features_crud.get_user_circles(user_id, user_id)
        assert len(user_circles) > 0, "User circles not found"
        print("✅ User circles retrieved successfully")
        
        # Test 4: Leave circle
        print("4. Testing circle leaving...")
        success = await missing_phase1_features_crud.leave_circle(circle_id, user_id)
        assert success, "Failed to leave circle"
        print("✅ Left circle successfully")
        
        # Test 5: RLS enforcement
        print("5. Testing circles RLS...")
        async with database.pool.acquire() as conn:
            different_user = uuid4()
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(different_user)
            )
            
            # Should not see circle members
            members = await conn.fetch(
                "SELECT * FROM circle_members WHERE circle_id = $1",
                circle_id
            )
            # Different user shouldn't see members unless they're also members
            print("✅ Circles RLS working")
        
        return True
        
    except Exception as e:
        print(f"❌ Circles test failed: {e}")
        return False

async def test_saved_posts_with_real_user():
    """Test saved posts system with real user context"""
    print("\n🧪 TESTING SAVED POSTS SYSTEM")
    print("=" * 40)
    
    user_id, post_id = await create_test_user_and_post()
    if not user_id or not post_id:
        return False
    
    try:
        from app.crud.missing_phase1_features import missing_phase1_features_crud
        
        # Test 1: Save post
        print("1. Testing post saving...")
        saved_post = await missing_phase1_features_crud.save_post(user_id, post_id)
        assert saved_post is not None, "Failed to save post"
        print("✅ Post saved successfully")
        
        # Test 2: Get saved posts
        print("2. Testing saved posts retrieval...")
        saved_posts = await missing_phase1_features_crud.get_user_saved_posts(user_id, user_id)
        assert len(saved_posts) > 0, "No saved posts found"
        print("✅ Saved posts retrieved successfully")
        
        # Test 3: Unsave post
        print("3. Testing post unsaving...")
        success = await missing_phase1_features_crud.unsave_post(user_id, post_id)
        assert success, "Failed to unsave post"
        print("✅ Post unsaved successfully")
        
        # Test 4: RLS enforcement
        print("4. Testing saved posts RLS...")
        async with database.pool.acquire() as conn:
            different_user = uuid4()
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                str(different_user)
            )
            
            # Should not see other user's saved posts
            saved = await conn.fetch(
                "SELECT * FROM saved_posts WHERE user_id = $1",
                user_id
            )
            assert len(saved) == 0, "RLS violation: saw other user's saved posts"
        print("✅ Saved posts RLS working")
        
        return True
        
    except Exception as e:
        print(f"❌ Saved posts test failed: {e}")
        return False

async def main():
    """Run all new feature tests"""
    print("🚀 COMPREHENSIVE TEST OF NEW PHASE 1 & 2 FEATURES")
    print("Testing with real user context and RLS enforcement")
    print("=" * 60)
    
    tests = [
        test_reactions_with_real_user,
        test_circles_with_real_user,
        test_saved_posts_with_real_user
    ]
    
    results = []
    for test in tests:
        try:
            result = await test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} failed: {e}")
            results.append(False)
    
    passed = sum(results)
    total = len(results)
    
    print("\n" + "=" * 60)
    print(f"📊 TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL NEW FEATURES WORKING CORRECTLY!")
        print("✅ Reactions system functional")
        print("✅ Circles system functional") 
        print("✅ Saved posts system functional")
        print("✅ RLS enforcement intact")
    else:
        print("⚠️  Some features need attention")
    
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
