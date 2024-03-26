window.addEventListener("load", async e => {
    // Define a function to fetch game time
    async function fetchGameTime() {
        try {
            const response = await fetch('/game-time');
            const data = await response.json();
            const serverTime = new Date(data.time);

            // Set the initial game time
            updateGameTime(serverTime);

            // Call updateGameTime every second
            setInterval(() => {
                const currentTime = new Date(); // Current client time
                const elapsedTime = currentTime - serverTime; // Elapsed time since server synchronization
                const timeToUpdate = 5 * 60 * 1000 - elapsedTime; // Time until next server synchronization (5 minutes - elapsed time)

                if (timeToUpdate <= 0) {
                    fetchGameTime(); // Call fetchGameTime to synchronize with the server
                } else {
                    updateGameTime(new Date(serverTime.getTime() + elapsedTime)); // Update game time based on elapsed time
                }
            }, 1000); // 1000 milliseconds = 1 second
        } catch (error) {
            console.error('Error fetching game time:', error);
            document.getElementById('game_time').innerHTML = 'Error fetching game time';
        }
    }

    // Define a function to update the game time displayed on the webpage
    function updateGameTime(gameTime) {
        // Extract hours, minutes, and seconds from the gameTime Date object
        const hours = gameTime.getHours().toString().padStart(2, '0');
        const minutes = gameTime.getMinutes().toString().padStart(2, '0');
        const seconds = gameTime.getSeconds().toString().padStart(2, '0');

        // Format the time in military format (24-hour format)
        const militaryTime = `${hours}:${minutes}:${seconds}`;

        document.getElementById('game_time').innerHTML = `
            Game TIME: ${militaryTime}
        `;
    }

    // Call fetchGameTime initially
    await fetchGameTime();
});
