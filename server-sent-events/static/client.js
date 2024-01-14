(function () {
    var eventSource = new EventSource("/events");

    eventSource.onmessage = function(event) {
        console.log(event);
        var element = document.getElementById("message");
        element.innerHTML = event.data;
        console.log("Data:", JSON.parse(event.data));
    }

    eventSource.onerror = function(err) {
        console.error("EventSource failed:", err);
    }
})()
