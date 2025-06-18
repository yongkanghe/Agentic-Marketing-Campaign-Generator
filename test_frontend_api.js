// Test script to simulate frontend API calls for image generation
// This will help us identify the exact issue causing "Network Error"

const axios = require('axios');

async function testImageGeneration() {
    console.log('🧪 Testing Frontend API Call for Image Generation...\n');
    
    try {
        // Simulate the exact API call the frontend makes
        const requestData = {
            post_type: 'text_image',
            regenerate_count: 2,
            business_context: {
                company_name: 'illustraMan',
                objective: 'Promote Joker t-shirt design',
                campaign_type: 'product',
                target_audience: 'business professionals',
                business_description: 'Digital artist creating pop culture inspired t-shirt designs',
                business_website: '',
                product_service_url: 'https://www.redbubble.com/i/t-shirt/The-Joker-Why-Aren-t-You-Laughing-by-illustraMan/170001221.1AP75',
                campaign_media_tuning: 'Dark, edgy pop culture style with comic book aesthetics'
            },
            creativity_level: 8
        };

        console.log('📤 Sending request to:', 'http://localhost:8000/api/v1/content/regenerate');
        console.log('📋 Request data:', JSON.stringify(requestData, null, 2));
        
        const startTime = Date.now();
        
        const response = await axios.post('http://localhost:8000/api/v1/content/regenerate', requestData, {
            timeout: 45000,
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const processingTime = Date.now() - startTime;
        
        console.log('\n✅ SUCCESS!');
        console.log('⏱️  Processing time:', processingTime, 'ms');
        console.log('📊 Response status:', response.status);
        console.log('🎯 Generated posts:', response.data.new_posts?.length || 0);
        
        if (response.data.new_posts && response.data.new_posts.length > 0) {
            const firstPost = response.data.new_posts[0];
            console.log('\n📄 First Generated Post:');
            console.log('  ID:', firstPost.id);
            console.log('  Type:', firstPost.type);
            console.log('  Content:', firstPost.content);
            console.log('  Image URL:', firstPost.image_url);
            console.log('  Hashtags:', firstPost.hashtags);
        }
        
        console.log('\n🎉 Frontend API call simulation SUCCESSFUL - No Network Error!');
        
    } catch (error) {
        console.log('\n❌ ERROR CAUGHT - This is likely what the frontend is experiencing:');
        
        if (error.code === 'ECONNABORTED') {
            console.log('🕒 TIMEOUT ERROR - Request took longer than 45 seconds');
        } else if (error.response) {
            console.log('📡 HTTP ERROR:');
            console.log('  Status:', error.response.status);
            console.log('  Status Text:', error.response.statusText);
            console.log('  Data:', error.response.data);
        } else if (error.request) {
            console.log('🌐 NETWORK ERROR - No response received');
            console.log('  Error message:', error.message);
        } else {
            console.log('🔥 GENERAL ERROR:', error.message);
        }
        
        console.log('\n🔍 This is the root cause of the "Network Error" in the frontend!');
    }
}

// Run the test
testImageGeneration(); 