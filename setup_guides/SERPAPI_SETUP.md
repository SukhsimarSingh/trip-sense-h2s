# SerpAPI Integration Setup Guide

## Overview

Trip Sense integrates with **SerpAPI** to provide real-time booking capabilities directly within the app. This eliminates the need for users to visit multiple websites to compare prices and make bookings.

### What is SerpAPI?

SerpAPI is a real-time API that scrapes search engine results from Google Flights, Google Hotels, and other Google services. It provides structured, reliable data for building booking integrations.

## Features

### ✈️ Real-time Flight Search
- Live flight prices from multiple airlines
- Departure and arrival times
- Flight duration and layover information
- Number of stops (direct, 1 stop, 2+ stops)
- Airline information and flight numbers
- Booking links to airline websites

### 🏨 Real-time Hotel Search
- Current hotel availability and rates
- Star ratings and guest reviews
- Detailed amenities (WiFi, pool, breakfast, etc.)
- Price per night and total stay cost
- Location and proximity to attractions
- Direct booking links

### 💰 Automatic Cost Estimation
- Budget breakdown by category:
  - Flights (per person)
  - Hotels (per night × nights)
  - Activities (per day × days)
  - Local transport (per day × days)
- Total cost calculation for all travelers
- Supports three budget levels: Budget, Medium, Luxury

### 👥 Multi-Traveler Support
- Collect information for entire travel party
- Individual traveler details (name, age, gender)
- Group booking cost calculations
- Primary contact management

## Setup Instructions

### 1. Get SerpAPI Key
1. Visit [SerpAPI.com](https://serpapi.com/)
2. Sign up for a free account
3. Navigate to your dashboard
4. Copy your API key

### 2. Add API Key to Environment
Add your SerpAPI key to your `.env` file:

```env
SERPAPI_API_KEY=your_api_key_here
```

### 3. Install Required Package
The package is already in `requirements.txt`, but if you need to install it manually:

```bash
pip install google-search-results
```

### 4. Restart the App
After adding the API key, restart your Streamlit app:

```bash
streamlit run streamlit_app.py
```

## Usage

### Booking Flow

1. **Select Trip**: Choose a trip from the dropdown on the Book page

2. **Enter Traveler Information**:
   - Fill in primary contact details
   - Add information for all travelers (if group size > 1)
   - Click "💾 Save Traveler Information"

3. **View Estimated Costs**:
   - Expand the "💰 Estimated Booking Cost" section
   - See breakdown by category (flights, hotels, activities, transport)
   - Total estimate shown for all travelers

4. **Search Real-Time Flights**:
   - Open the "Flights" step
   - Click "🔍 Find Real-Time Flights"
   - View top flight options with:
     - Airlines
     - Departure/Arrival times
     - Duration
     - Number of stops
     - Prices

5. **Search Real-Time Hotels**:
   - Open the "Accommodation" step
   - Click "🔍 Find Real-Time Hotels"
   - View top hotel options with:
     - Hotel names
     - Ratings and reviews
     - Amenities
     - Price per night and total cost

### Demo Mode

If SerpAPI is not configured or the quota is exceeded, the app automatically falls back to **demo mode**:

- 📊 Shows realistic sample data for flights and hotels
- ⚠️ Displays warning banner indicating demo mode
- 🎨 Allows UI/UX testing without API costs
- ✅ Perfect for development and demonstrations

**Note**: Demo data is static and doesn't reflect real prices or availability.

## API Limits & Pricing

### Free Tier (SerpAPI)
- **100 searches/month** for free
- Sufficient for testing and small-scale use
- Includes Google Flights and Google Hotels

### Paid Plans
- **Basic**: $50/month - 5,000 searches
- **Standard**: $150/month - 20,000 searches
- **Advanced**: $300/month - 50,000 searches

Learn more at: [https://serpapi.com/pricing](https://serpapi.com/pricing)

## Features in Detail

### Multi-Traveler Information
```python
# Example saved traveler data structure:
{
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+1234567890",
    "country": "United States",
    "group_size": 3,
    "passengers": [
        {"name": "John Doe", "age": 35, "gender": "Male"},
        {"name": "Jane Doe", "age": 32, "gender": "Female"},
        {"name": "Jimmy Doe", "age": 8, "gender": "Male"}
    ]
}
```

### Cost Estimation Logic
```python
# Base costs per person per category
Budget: {
    'flight': $200, 'hotel': $50/night, 
    'activity': $30/day, 'transport': $20/day
}
Medium Budget: {
    'flight': $400, 'hotel': $100/night,
    'activity': $60/day, 'transport': $40/day
}
Luxury: {
    'flight': $800, 'hotel': $250/night,
    'activity': $150/day, 'transport': $80/day
}
```

## Troubleshooting

### Issue: "SerpAPI not configured" warning
**Solution**: Add `SERPAPI_API_KEY` to your `.env` file and restart the app

### Issue: No flight results shown
**Solution**: 
- Verify your API key is correct
- Check your API usage limits
- Ensure dates are in YYYY-MM-DD format

### Issue: Hotel search returns no results
**Solution**:
- Verify the destination city name is correct
- Try using a more general location (e.g., "Paris" instead of "Paris 8th Arrondissement")
- Check your API key has sufficient quota

### Issue: "Library not installed" error
**Solution**: 
```bash
pip install google-search-results
```

## Code Structure

### New Files
- `services/serpapi_service.py`: Core SerpAPI integration
  - `search_flights()`: Search for flights
  - `search_hotels()`: Search for hotels
  - `get_demo_flights()`: Demo data fallback
  - `get_demo_hotels()`: Demo data fallback

### Modified Files
- `pages/book.py`: 
  - Multi-traveler information collection
  - Estimated cost calculation
  - Real-time flight/hotel search integration
  - Trip-specific progress tracking

- `requirements.txt`:
  - Added `google-search-results` package

## Example API Responses

### Flight Search Response
```json
{
    "success": true,
    "best_flights": [
        {
            "price": "$450",
            "airline": "United Airlines",
            "departure_time": "10:00 AM",
            "arrival_time": "2:00 PM",
            "duration": "4h",
            "stops": []
        }
    ]
}
```

### Hotel Search Response
```json
{
    "success": true,
    "hotels": [
        {
            "name": "Hilton Downtown",
            "rate_per_night": "$120",
            "total_rate": "$360",
            "rating": 4.5,
            "reviews": 1250,
            "amenities": ["WiFi", "Pool", "Breakfast"]
        }
    ]
}
```

## Best Practices

### API Usage Optimization

1. **Cache Results**: Store search results temporarily to avoid redundant queries
2. **Rate Limiting**: Implement delays between consecutive searches
3. **Error Handling**: Always have fallback to demo mode
4. **User Feedback**: Show loading states during API calls
5. **Quota Monitoring**: Track API usage to avoid unexpected overages

### Cost Management

**Tips to Minimize API Costs:**

1. **Use Demo Mode for Development**: Test UI with demo data
2. **Implement Caching**: Cache search results for 15-30 minutes
3. **Batch Similar Requests**: Group searches when possible
4. **Set Search Limits**: Limit number of results returned (e.g., top 5)
5. **Monitor Usage**: Check SerpAPI dashboard regularly
6. **Enable Alerts**: Set up quota warnings

### Security

1. ✅ Never expose API key in client-side code
2. ✅ Store API key in environment variables
3. ✅ Use `.env` file (gitignored) for local development
4. ✅ Use Secret Manager for production deployment
5. ✅ Rotate API keys periodically
6. ✅ Set up IP restrictions if possible

## Performance Tips

### Optimize Search Parameters

**Flight Searches:**
- Use IATA airport codes (e.g., "JFK" instead of "New York")
- Specify dates in YYYY-MM-DD format
- Limit results to top 5-10 flights
- Cache results for at least 1 hour

**Hotel Searches:**
- Use specific city names
- Include check-in and check-out dates
- Filter by minimum rating if needed
- Cache results for 4-6 hours (prices change less frequently)

### Handle Rate Limits

```python
import time

def search_with_retry(search_function, max_retries=3):
    for attempt in range(max_retries):
        try:
            return search_function()
        except RateLimitError:
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 5  # 5, 10, 15 seconds
                time.sleep(wait_time)
            else:
                return get_demo_data()  # Fallback to demo
```

## Integration Architecture

### How It Works

1. **User Initiates Search**
   - User clicks "Find Real-Time Flights" or "Find Real-Time Hotels"
   - App validates trip details (dates, destination, travelers)

2. **API Request**
   - App calls SerpAPI with search parameters
   - Backend service handles authentication and formatting

3. **Data Processing**
   - Parse SerpAPI JSON response
   - Extract relevant fields (price, airline, rating, etc.)
   - Format data for display

4. **Display Results**
   - Show top results in user-friendly cards
   - Provide booking links
   - Display pricing per traveler and total

5. **Fallback Handling**
   - If API fails or quota exceeded → demo mode
   - If no results found → show helpful message
   - If invalid parameters → show validation errors

### Data Flow

```
┌─────────────┐         ┌──────────────┐         ┌──────────────┐
│   User UI   │────────>│ Streamlit    │────────>│   SerpAPI    │
│  (Book      │         │  Backend     │         │   Service    │
│   Page)     │         │ (serpapi_    │         │              │
│             │         │  service.py) │         │              │
└─────────────┘         └──────────────┘         └──────────────┘
      ▲                        │                         │
      │                        │                         │
      │                        ▼                         ▼
      │                 ┌──────────────┐         ┌──────────────┐
      └─────────────────│  Format &    │<────────│ Google       │
                        │  Display     │         │ Flights/     │
                        │  Results     │         │ Hotels       │
                        └──────────────┘         └──────────────┘
```

## Advanced Features

### Custom Search Parameters

Customize searches based on user preferences:

```python
# Example: Premium cabin class search
search_params = {
    'departure': 'JFK',
    'arrival': 'LAX',
    'date': '2025-12-01',
    'return_date': '2025-12-08',
    'adults': 2,
    'travel_class': '2',  # 1=Economy, 2=Premium Economy, 3=Business, 4=First
    'max_stops': 1
}
```

### Filter and Sort

```python
# Filter hotels by rating
hotels = [h for h in results if h.get('rating', 0) >= 4.0]

# Sort by price
sorted_hotels = sorted(hotels, key=lambda x: x.get('price', float('inf')))

# Sort flights by duration
sorted_flights = sorted(flights, key=lambda x: x.get('duration_minutes', 0))
```

### Price Tracking

Implement price tracking for repeat searches:

```python
# Store previous search results
previous_price = get_cached_price(search_key)
current_price = current_search_result['price']

if current_price < previous_price:
    show_price_drop_alert(previous_price, current_price)
```

## Production Checklist

Before deploying to production:

- [ ] API key stored in environment variables
- [ ] Demo mode fallback implemented
- [ ] Error handling for all API calls
- [ ] Loading states displayed during searches
- [ ] Results cached to minimize API calls
- [ ] Rate limiting implemented
- [ ] Quota monitoring set up
- [ ] User feedback for errors (friendly messages)
- [ ] HTTPS enforced for all API calls
- [ ] API key rotation schedule established
- [ ] Cost alerts configured in SerpAPI dashboard
- [ ] Usage analytics tracking implemented

## Monitoring & Analytics

### Track Key Metrics

1. **API Usage**
   - Number of searches per day
   - Success rate (successful vs failed requests)
   - Average response time
   - Cache hit rate

2. **User Behavior**
   - Most searched destinations
   - Average price ranges
   - Booking conversion rate (searches → bookings)
   - Most popular travel dates

3. **Cost Analysis**
   - API cost per search
   - Total monthly API spend
   - Cost per user acquisition
   - ROI on SerpAPI integration

### SerpAPI Dashboard

Monitor usage in your SerpAPI dashboard:
1. Visit [https://serpapi.com/dashboard](https://serpapi.com/dashboard)
2. View real-time usage statistics
3. Check remaining quota
4. Review API call history
5. Analyze response times

## Alternatives to SerpAPI

If SerpAPI doesn't fit your needs, consider:

1. **Amadeus API**: Official airline and hotel data (requires approval)
2. **Skyscanner API**: Flight and hotel search (limited free tier)
3. **Google Flights API**: Direct Google integration (complex setup)
4. **Booking.com API**: Hotel bookings (affiliate program)
5. **Kayak API**: Multi-source travel search (business accounts)

**Note**: SerpAPI is recommended for Trip Sense due to ease of integration and reliable data quality.

## Support & Resources

### Documentation
- **SerpAPI Documentation**: [https://serpapi.com/docs](https://serpapi.com/docs)
- **Google Flights API Docs**: [https://serpapi.com/google-flights-api](https://serpapi.com/google-flights-api)
- **Google Hotels API Docs**: [https://serpapi.com/google-hotels-api](https://serpapi.com/google-hotels-api)

### Code Examples
- **Python Client**: [https://github.com/serpapi/google-search-results-python](https://github.com/serpapi/google-search-results-python)
- **Example Projects**: [https://serpapi.com/examples](https://serpapi.com/examples)

### Support Channels
- **Email Support**: support@serpapi.com
- **Community Forum**: [https://forum.serpapi.com/](https://forum.serpapi.com/)
- **GitHub Issues**: [https://github.com/serpapi/google-search-results-python/issues](https://github.com/serpapi/google-search-results-python/issues)

### Trip Sense Specific
- **Implementation**: See `services/serpapi_service.py`
- **Booking Page**: See `pages/book.py`
- **Demo Functions**: `get_demo_flights()`, `get_demo_hotels()`

---

**🎉 Happy Booking! ✈️🏨**

Your users can now search and book flights and hotels without leaving your app!

