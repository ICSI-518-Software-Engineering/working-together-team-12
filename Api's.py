def movies_home(request):
    time.sleep(2)
    latest_selection = CitySelection.objects.filter(user=request.user).order_by('-created').first()
    print('latest_selection in movies',latest_selection)
    data={}
    if latest_selection is not None:

        parts = latest_selection.city_name.split(',')
        if len(parts) >= 2:
            city_name = parts[0].strip()  
            state_name = parts[1].strip() 
        matching_city = City.objects.filter(city_name=city_name, state_name=state_name).first()    
        if matching_city:
                    data = {
                        'city_name': matching_city.city_name,
                        'state_name': matching_city.state_name,
                        'latitude': str(matching_city.lat),
                        'longitude': str(matching_city.lng)
                    }
    else:
         data = {
                        'city_name': 'Albany',
                        'state_name': 'New York',
                        'latitude': '42.6664"',
                        'longitude': '-73.7987'
                    }                 
    print(data)
    theaters_url = "https://flixster.p.rapidapi.com/theaters/list"  

    theaters_query = {"latitude":data['latitude'],"longitude":data['longitude'], "radius": "50"}
    print('theaters_query',theaters_query)
    theaters_headers = {
        'X-RapidAPI-Key': '45a930506emsh6549e47dbad2b62p1e6fa6jsnbe1866f01c8b', 
        "X-RapidAPI-Host": "flixster.p.rapidapi.com"
    }
    print("It got pushed")