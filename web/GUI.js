// **** GUI for Tic Tac Toe ****

// TO-DO:

// DONE:

var square = new Array(9);

for (var i = 0; i < 9; ++i) {
	square[i] = document.getElementById('T' + i.toString());

	square[i].addEventListener('click', (e) => {
		const td = e.currentTarget;
		if (td.innerText == '')
			td.innerText = 'X';
		else if (td.innerText == 'X')
			td.innerText = 'O';
		else
			td.textContent = '';
		td.className = td.innerText;
		});
	}

// ***************** SSE handling ********************

function streamEventHandler(e) {
	var s = JSON.parse(e.data);
	// console.log("s.data =" + s.data);
	for (var i = 0; i < 9; ++i) {
		square[i].innerText = s.data[i];
		square[i].className = s.data[i];
		}
	}

var evtSource = null;

// evtSource = new EventSource("http://localhost:7000/SSE");

// evtSource.onmessage = streamEventHandler;

/*
evtSource.onerror = function(e) {
	if (evtSource.readyState == 2) {
		evtSource.close();
		setTimeout(initEventSource, 5000);
		}
	};
*/

console.log("Event source established");

function initEventSource() {
	// Listen to Node.js server
	evtSource = new EventSource("http://localhost:7000/SSE");
	// evtSource = new EventSource("localhost:6379/stream");
	evtSource.onmessage = streamEventHandler;
	evtSource.onerror = function(e) {
		if (evtSource.readyState == 2) {
			evtSource.close();
			setTimeout(initEventSource, 3000);
			}
		};
	console.log("Event source established");
	}

// ***************** Keyboard Buttons *****************



// ******************* Menu Buttons *******************

document.getElementById("train").addEventListener("click", function() {
	$.ajax({
	method: "GET",
	url: "/evolve",
	cache: false,
	success: function(resp) {
		// console.log("Started evolve.");
		console.log(resp);
		const audio = new Audio("sending.ogg");
		audio.play();
		}});
	});
