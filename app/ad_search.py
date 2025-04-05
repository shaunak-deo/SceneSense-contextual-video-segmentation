import os
import json
import random
import requests
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Google Custom Search API credentials
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")

def search_ads_for_labels(labels):
    """
    Search for relevant video ads based on segment labels using Google Custom Search API.
    Falls back to sample ads if API fails.
    """
    # Sample ads database as fallback
    SAMPLE_ADS = {
        "food": [
            {
                "title": "Gourmet Kitchen Experience",
                "description": "Discover our premium kitchen appliances for the perfect cooking experience.",
                "image_url": "https://images.unsplash.com/photo-1556911220-bff31c812dba?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60",
                "video_url": ""
            },
            {
                "title": "Restaurant Style Cooking",
                "description": "Learn professional cooking techniques with our expert chefs.",
                "image_url": "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60",
                "video_url": ""
            }
        ],
        "home": [
            {
                "title": "Modern Living Spaces",
                "description": "Transform your home with our contemporary furniture collection.",
                "image_url": "https://images.unsplash.com/photo-1616486338812-3dadae4b4ace?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60",
                "video_url": ""
            },
            {
                "title": "Cozy Home Decor",
                "description": "Create a warm and inviting atmosphere with our home decor items.",
                "image_url": "https://images.unsplash.com/photo-1615873968403-89e068629265?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60",
                "video_url": ""
            }
        ],
        "nightlife": [
            {
                "title": "Urban Nightlife Experience",
                "description": "Experience the city's vibrant nightlife with our exclusive venues.",
                "image_url": "https://images.unsplash.com/photo-1516450360452-9312f5e86fc7?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60",
                "video_url": ""
            },
            {
                "title": "City Entertainment Guide",
                "description": "Discover the best entertainment spots in the city.",
                "image_url": "https://images.unsplash.com/photo-1519671482749-fd09be7ccebf?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60",
                "video_url": ""
            }
        ]
    }
    
    relevant_ads = []
    
    # Extract keywords from labels
    keywords = []
    for label_group in labels:
        # Split by comma and clean up
        for label in label_group.split(','):
            keyword = label.strip().lower()
            if keyword:
                keywords.append(keyword)
    
    # If no keywords found, return empty list
    if not keywords:
        return []
    
    # Try to find matching ads from sample database first
    for keyword in keywords:
        for category, ads in SAMPLE_ADS.items():
            if category in keyword:
                relevant_ads.extend(ads)
    
    # If we found sample ads, return them
    if relevant_ads:
        # Remove duplicates
        unique_ads = []
        seen_titles = set()
        for ad in relevant_ads:
            if ad["title"] not in seen_titles:
                seen_titles.add(ad["title"])
                unique_ads.append(ad)
        
        # Return up to 3 unique ads
        return unique_ads[:3]
    
    # If no sample ads found, try Google Custom Search API
    # Use the most relevant keywords (up to 3) for the search
    search_keywords = keywords[:3]
    
    # Create a simpler search query
    search_query = " ".join(search_keywords) + " advertisement"
    
    try:
        # Make API request to Google Custom Search
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": GOOGLE_API_KEY,
            "cx": GOOGLE_CSE_ID,
            "q": search_query,
            "num": 5,  # Get 5 results
            "safe": "active"  # Safe search
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise exception for HTTP errors
        
        data = response.json()
        
        # Process search results
        if "items" in data:
            for item in data["items"]:
                # Extract information
                title = item.get("title", "").split(" - ")[0]  # Take first part of title
                description = item.get("snippet", "")
                
                # Get thumbnail
                image_url = ""
                if "pagemap" in item and "cse_thumbnail" in item["pagemap"]:
                    image_url = item["pagemap"]["cse_thumbnail"][0].get("src", "")
                
                # Get URL
                url = item.get("link", "")
                
                # Create ad object
                ad = {
                    "title": title,
                    "description": description,
                    "image_url": image_url,
                    "video_url": url
                }
                
                # Only add if we have at least an image or URL
                if image_url or url:
                    relevant_ads.append(ad)
            
            # If we found ads, return them
            if relevant_ads:
                # Remove duplicates
                unique_ads = []
                seen_titles = set()
                for ad in relevant_ads:
                    if ad["title"] not in seen_titles:
                        seen_titles.add(ad["title"])
                        unique_ads.append(ad)
                
                # Return up to 3 unique ads
                return unique_ads[:3]
                
    except Exception as e:
        print(f"Error searching for ads with query '{search_query}': {e}")
    
    # If all else fails, return random sample ads
    all_sample_ads = []
    for ads in SAMPLE_ADS.values():
        all_sample_ads.extend(ads)
    
    return random.sample(all_sample_ads, min(3, len(all_sample_ads)))

def generate_ai_ads(labels):
    """
    Use OpenAI to generate ad suggestions based on segment labels.
    """
    try:
        # Combine all labels into a single string
        all_labels = ", ".join(labels)
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an advertising expert. Generate 3 relevant video ad suggestions based on the given labels."},
                {"role": "user", "content": f"Generate 3 video ad suggestions for a video segment with these labels: {all_labels}. Format as JSON with title, description, image_url, and video_url fields. Make the ads highly relevant to the content."}
            ],
            max_tokens=300
        )
        
        # Parse the response
        content = response.choices[0].message.content
        
        # Try to extract JSON from the response
        try:
            # Find JSON in the response
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            if start_idx >= 0 and end_idx > start_idx:
                json_str = content[start_idx:end_idx]
                ads = json.loads(json_str)
                return ads
            else:
                # If no JSON found, return empty list
                return []
        except json.JSONDecodeError:
            # If JSON parsing fails, return empty list
            return []
            
    except Exception as e:
        print(f"Error generating AI ads: {e}")
        # Return empty list
        return [] 