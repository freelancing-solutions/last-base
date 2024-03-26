
window.addEventListener("load", async e => {
    // Define a function to fetch game time
    async function fetchGameTime() {
        try {
            const response = await fetch('/game-time');
            const data = await response.json();
            const game_time = new Date(data.time);

            // Extract hours, minutes, and seconds from the game_time Date object
            const hours = game_time.getHours().toString().padStart(2, '0');
            const minutes = game_time.getMinutes().toString().padStart(2, '0');
            const seconds = game_time.getSeconds().toString().padStart(2, '0');

            // Format the time in military format (24-hour format)
            const militaryTime = `${hours}:${minutes}:${seconds}`;

            document.getElementById('game_time').innerHTML = `
                Game TIME: <span class="font-weight-bold"> ${militaryTime}</span>
            `;
        } catch (error) {
            console.error('Error fetching game time:', error);
            document.getElementById('game_time').innerHTML = 'Error fetching game time';
        }
    }

    // Call fetchGameTime initially
    await fetchGameTime();

    // Call fetchGameTime every minute
    setInterval(fetchGameTime, 600); // 60000 milliseconds = 1 minute
});
