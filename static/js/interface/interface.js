window.addEventListener("load", async e => {
    // Define global variables to hold server time and interval ID
    let serverTime;
    let intervalId;

    // Define a function to fetch game time from the server
    async function fetchGameTime() {
        console.log("calling the server again");
        try {
            const response = await fetch('/game-time');
            const data = await response.json();
            serverTime = new Date(data.time);
        } catch (error) {
            console.error('Error fetching game time:', error);
            document.getElementById('game_time').innerHTML = 'Error fetching game time';
        }
    }

    // Define a function to update the game time displayed on the webpage
    function updateGameTime() {
        // Add one second to the current displayed time
        serverTime.setSeconds(serverTime.getSeconds() + 1);

        // Extract hours, minutes, and seconds from the serverTime Date object
        const hours = serverTime.getHours().toString().padStart(2, '0');
        const minutes = serverTime.getMinutes().toString().padStart(2, '0');
        const seconds = serverTime.getSeconds().toString().padStart(2, '0');

        // Format the time in military format (24-hour format)
        const militaryTime = `${hours}:${minutes}:${seconds}`;

        document.getElementById('game_time').innerHTML = `
            <span class="font-weight-bold text-danger">GAME TIME</span> :<span class="font-weight-bold">${militaryTime}</span>
        `;
    }

    // Fetch game time from the server initially
    await fetchGameTime();

    // Call updateGameTime every second
    intervalId = setInterval(() => {
        updateGameTime();

        // Check if 5 minutes have elapsed
        const elapsedTime = new Date() - serverTime;
        if (elapsedTime >= 5 * 60 * 100000) { // 5 minutes in milliseconds
            clearInterval(intervalId); // Stop the current interval
            fetchGameTime(); // Fetch game time from the server again
        }
    }, 1000); // 1000 milliseconds = 1 second
});
