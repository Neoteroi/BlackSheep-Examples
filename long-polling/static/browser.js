// Sending messages, a simple POST
function PublishForm(form, url) {

    function sendMessage(message) {
        fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ text: message })
        });
    }

    form.onsubmit = function() {
        let message = form.message.value;
        if (message) {
        form.message.value = '';
        sendMessage(message);
        }
        return false;
    };
}

// Receiving messages with long polling
function SubscribePane(elem, url) {

    function showMessage(message) {
        let messageElem = document.createElement('div');
        messageElem.append(message);
        elem.append(messageElem);
    }

    async function subscribe() {
        let response = await fetch(url).catch(() => {
            // This can happen if the server restarts,
            // we need to try again polling
            setTimeout(() => {
                subscribe();
            }, 5000);
            return;
        });

        if (response.status == 502) {
            // Connection timeout
            // happens when the connection was pending for too long
            // let's reconnect
            await subscribe();
        } else if (response.status != 200) {
            // Show Error
            showMessage(response.statusText);
            // Reconnect in one second
            await new Promise(resolve => setTimeout(resolve, 1000));
            await subscribe();
        } else {
            // Got message
            let message = await response.text();
            showMessage(message);
            await subscribe();
        }
    }

    subscribe();
}
