def search_flights(request):
    if request.method == 'POST':
        origin = request.POST.get('origin')
        destination = request.POST.get('destination')
        departure_date = request.POST.get('departure_date')
        sort_order = request.POST.get('sort_order')
        class_type = request.POST.get('class_type')
        print("origin is", origin)
        print("destination is", destination)
        headers = {
            "X-RapidAPI-Key": "7dbc098597msh8dfc40d52e8a0fcp173ffejsneb6d1efbdb5d",
            "X-RapidAPI-Host": "priceline-com-provider.p.rapidapi.com"
        }
        origin_response = requests.get(
            "https://priceline-com-provider.p.rapidapi.com/v1/flights/locations",
            headers=headers, params={"name": origin}
        )
        print('origin',origin_response.json()[0]['id'])
        destination_response = requests.get(
            "https://priceline-com-provider.p.rapidapi.com/v1/flights/locations",
            headers=headers, params={"name": destination}
        )
        print('origin',destination_response.json()[0]['id'])
        
        if origin_response.ok and destination_response.ok:
            origin_id = origin_response.json()[0]['id']
            destination_id = destination_response.json()[0]['id']
            print(origin_id,destination_id)

            # Redirect to the flight results page, passing necessary information
            return redirect('flight_results', origin_id=origin_id, destination_id=destination_id, date=departure_date, sort_order=sort_order,class_type=class_type)
        else:
            error_message = "There was a problem finding the locations. Please try again."
            return render(request, 'search_flights.html', {'error_message': error_message})

    return render(request, 'flights_home.html')