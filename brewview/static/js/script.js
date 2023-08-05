function fetchPubData() {
    let city = document.getElementById('cityDropdown').value;
    fetch(`/fetch_pubs/${city}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            let tableBody = document.getElementById('priceTable').getElementsByTagName('tbody')[0];
            tableBody.innerHTML = '';  // Clear the current table data

            // Variables to calculate average
            let sum = 0;
            let count = 0;

            data.forEach(pub => {
                let row = tableBody.insertRow();
                let nameCell = row.insertCell(0);
                let guinnessCell = row.insertCell(1);
                let tennantCell = row.insertCell(2);
                let ipaCell = row.insertCell(3);

                nameCell.textContent = pub.name;
                guinnessCell.textContent = pub.guinness !== 'N/A' ? '£' + pub.guinness : 'N/A';
                tennantCell.textContent = pub.tennant !== 'N/A' ? '£' + pub.tennant : 'N/A';
                ipaCell.textContent = pub.ipa !== 'N/A' ? '£' + pub.ipa : 'N/A';

                // Adding up prices for average calculation
                if (pub.guinness !== 'N/A') {
                    sum += pub.guinness;
                    count++;
                }
                if (pub.tennant !== 'N/A') {
                    sum += pub.tennant;
                    count++;
                }
                if (pub.ipa !== 'N/A') {
                    sum += pub.ipa;
                    count++;
                }
            });

            // Calculate average
            let average = sum / count;

            // Display average somewhere on the page
            // ...

            // Optionally, calculate and display the standard deviation
            // ...
        })
        .catch(error => {
            console.error('There has been a problem with your fetch operation:', error);
        });
}



function navigateToAddEntry() {
    window.location.href = "/add_entry";
}

