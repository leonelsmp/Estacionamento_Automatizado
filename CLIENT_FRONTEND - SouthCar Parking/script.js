// script.js
document.addEventListener('DOMContentLoaded', function () {
    const parkingLotElement = document.getElementById('parking-lot');
  
    function createParkingSlot(spotId, isOccupied) {
      const spotElement = document.createElement('div');
      spotElement.id = `spot-${spotId}`;
      spotElement.classList.add('spot', isOccupied ? 'occupied' : 'available');
      spotElement.textContent = isOccupied ? 'Occupied' : 'Available';
      parkingLotElement.appendChild(spotElement);
    }
  
    function updateParkingSpotDisplay(spotId, isOccupied) {
      const spotElement = document.getElementById(`spot-${spotId}`);
      if (spotElement) {
        spotElement.classList.remove('available', 'occupied', 'loading');
        spotElement.classList.add(isOccupied ? 'occupied' : 'available');
        // The text content can be adjusted here if you decide to add text indicators
        spotElement.textContent = isOccupied ? 'Occupied' : 'Available';
      } else {
        // If the spot doesn't exist, create it
        createParkingSlot(spotId, isOccupied);
      }
    }
  
    // Initial fetching of parking lot status
    fetch('https://southcarpark-api.onrender.com/Vagas') //'https://leonelsmp.pythonanywhere.com/Vagas'
      .then(response => response.json())
      .then(data => {
        // Create slots for the first time based on fetched data
        data.forEach(spot => {
          createParkingSlot(spot.Vagaid, spot.Ocupada);
        });
      })
      .catch(error => {
        console.error('Error fetching initial parking spot statuses:', error);
      });
  
    // Connect to the Socket.io server
    const socket = io('https://southcarpark-api.onrender.com/mynamespace');
  
    // Listen for 'update' event from the server
    socket.on('message', function(data) {
        console.log(data);
      if (data && data.Vagaid != null && data.Ocupada != null) {
        updateParkingSpotDisplay(data.Vagaid, data.Ocupada);
      }
    });

    socket.on('connect', function() {
        console.log('Connected to the socket server.');
      });
  });
  