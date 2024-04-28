// $(document).ready(function() {
//     // $('#cityPopup').show();
//     // $('body').addClass('blurred');

//     // $('.cityOption').click(function(e) {
//     //     e.preventdefault();
//     //     var selectedCity = $(this).val();
//     //     var currentDateTime = new Date().toISOString();     
//     //     var loc = selectedCity;
//     //     $('#cityDropdown').val(selectedCity).trigger('change');
//     //     $('#cityPopup').hide();
//     //     // $('body').removeClass('blurred');
//     //     console.log("button clicked");

//     //     $.ajax({
//     //         url: "https://api-gate2.movieglu.com/cinemasNearby/?n=5", 
//     //         method: "GET",
//     //         headers: {
//     //             "client": "PROJ_36",   
//     //             "x-api-key": "h5aonOtHaP8W4kPX3LKMz1Q9LT0ba5G56ely4V2g",
//     //             "authorization": "Basic UFJPSl8zNjpXb3VEMGhWY3BtZlQ=", 
//     //             "territory": "IN",
//     //             "api-version": "v200",
//     //             "geolocation": loc,
//     //             "device-datetime": currentDateTime,
//     //             },
//     //         success: function(response) {
//     //             console.log("clicked");
//     //             const cinemaIds = response.cinemas.map(cinema => cinema.cinema_id);
//     //             // For each cinema ID, fetch showtimes
//     //             $('#movies_now').empty();
//     //             cinemaIds.forEach(cinemaId => {
//     //                 const currentDate = new Date().toISOString().split('T')[0]; // Format as 'YYYY-MM-DD'
//     //                 console.log(cinemaId);
//     //                 fetchCinemaShowtimes(cinemaId, currentDate,loc);
//     //                 // console.log(cinemaId);
//     //             });
                
//     //         },
//     //         error: function(error) {
//     //             console.log("Error:", error);
//     //             console.log("clicked");

//     //         }
//     //         });
//     // });
    
 

// });
$(document).ready(function () {
    $("#searchButton").click(function(e) {
        e.preventDefault();
        var searchTerm = $(searchInput).val(); 
        var encodedSearchTerm = encodeURIComponent(searchTerm);
        var targetUrl = `https://api-gate2.movieglu.com/filmLiveSearch/?query=${encodedSearchTerm}&n=10`;
        var currentDateTime = new Date().toISOString();
        var selectedOption = $('#cityDropdown').find('option:selected');
        var loc = selectedOption.attr('class');
        console.log(targetUrl);
        $.ajax({
            url: targetUrl,
            method: "GET",
            timeout: 0,
            headers: {
                "client": "REQU",   
                "x-api-key": "ILPu1EKnTX30MHdMVJytO8dLCygblDqW7UebInXB",
                "authorization": "Basic UkVRVToweVI1cmxTaXEyOEY=", 
                "territory": "US",
                "api-version": "v200",
                "geolocation": loc,
                "device-datetime": currentDateTime,
                },
            success: function(data) {
            console.log("live seachdata: ",data);
            $.ajax({
                url: '/movie-search',
                method: 'POST',
                data: { films_data: JSON.stringify(data.films) },
                success: function(response) {
                    // console.log("Film data sent to server successfully.");
                    window.location.href = 'fetch-movies';
                },
                error: function(error) {
                    console.log("Error:", error);
                }
            });
            },
            error: function(error) {
                console.log("Error:", error);
            }
        });
    });
});
