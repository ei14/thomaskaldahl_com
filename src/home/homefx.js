const sensitivity = 0.01;
const updateTime = 132;
const drawTime = 66;
const alpha = 0.15;
const occasion = 24;

document.addEventListener("DOMContentLoaded", e => {
	// CHROMATIC ABERRATION

	const width = window.innerWidth;
	const height = window.innerHeight;

	var chrodiv = document.getElementById("chromatic");
	var chrotext = chrodiv.children[0];
	var copies = [];
	for(var i = 0; i < 3; i++) {
		copies.push(chrotext.cloneNode(true));
		copies[i].style.position = "absolute";
		copies[i].style.top = 0;
		copies[i].style.mixBlendMode = "screen";
		copies[i].style.textShadow = "0 0 1vh";
		chrodiv.appendChild(copies[i]);
	}
	chrotext.style.opacity = 0;

	copies[0].style.color = "#ff0000";
	copies[1].style.color = "#00ff00";
	copies[2].style.color = "#0000ff";

	copies[0].style.userSelect = "none";
	copies[1].style.userSelect = "none";

	document.addEventListener("mousemove", e => {
		copies[0].style.left = sensitivity * (e.clientX - 0.5*width) + "px";
		copies[0].style.top = sensitivity * (e.clientY - 0.5*height) + "px";

		copies[2].style.left = -sensitivity * (e.clientX - 0.5*width) + "px";
		copies[2].style.top = -sensitivity * (e.clientY - 0.5*height) + "px";
	});

	// CONWAY'S GAME OF LIFE

	// Add shaddow to text
	document.querySelectorAll("p").forEach(par => {
		par.style.textShadow = "0 0 1vh black, 0 0 1vh black, 0 0 1vh black, 0 0 1vh black";
	});

	const canvas = document.createElement("canvas");

	canvas.width = window.innerWidth;
	canvas.height = window.innerHeight;

	canvas.style.zIndex = -10;
	canvas.style.margin = 0;
	canvas.style.position = "fixed";
	canvas.style.top = 0;
	canvas.style.left = 0;
	canvas.style.height = "100vh";

	var ctx = canvas.getContext("2d");
	ctx.fillStyle = "black";
	ctx.fillRect(0, 0, canvas.width, canvas.height);
	ctx.globalAlpha = alpha;

	const rows = 32;
	const cols = Math.ceil(32 * canvas.width/canvas.height);
	const cellsize = canvas.height / rows;

	var board = [];
	var pboard = []; // Previous state of the board

	for(var r = 0; r < rows; r++) {
		var row = [];
		for(var c = 0; c < cols; c++) {
			var cell = Math.round(Math.random());
			row.push(cell);
		}
		board.push(row);
	}

	var oboard = board; // Board that only updates occasionally
	var frame = 0; // Frame number, modulo `occasion`

	var drawCanvas;
	setTimeout(() => {
		drawCanvas = setInterval(() => {
			for(var r = 0; r < rows; r++) {
				for(var c = 0; c < cols; c++) {
					var state = board[r][c] + pboard[r][c];
					switch(state) {
						case 0:
						ctx.fillStyle = "#000";
						break;

						case 1:
						ctx.fillStyle = "#111";
						break;

						case 2:
						ctx.fillStyle = "#222";
						break;
					}

					ctx.fillRect(c * cellsize, r * cellsize, cellsize, cellsize);
				}
			}
		}, drawTime);
	}, updateTime);

	const conway = setInterval(() => {
		pboard = board;
		board = [];

		for(var r = 0; r < rows; r++) {
			var row = [];
			for(var c = 0; c < cols; c++) {
				const sum = pboard[(r - 1 + rows) % rows][(c - 1 + cols) % cols]
					+ pboard[r][(c - 1 + cols) % cols]
					+ pboard[(r + 1) % rows][(c - 1 + cols) % cols]
					+ pboard[(r - 1 + rows) % rows][c]
					+ pboard[(r + 1) % rows][c]
					+ pboard[(r - 1 + rows) % rows][(c + 1) % cols]
					+ pboard[r][(c + 1) % cols]
					+ pboard[(r + 1) % rows][(c + 1) % cols]

				if(
					(pboard[r][c] == 0 && sum == 3)
					|| (pboard[r][c] == 1 && sum != 2 && sum != 3)
				) {
					row.push(1 - pboard[r][c]);
				} else {
					row.push(pboard[r][c]);
				}
			}
			board.push(row);
		}

		frame++;
		if(frame === occasion) {
			frame = 0;
			var stale = true;
			staleCheck:
			for(var r = 0; r < rows; r++) {
				for(var c = 0; c < cols; c++) {
					if(board[r][c] !== oboard[r][c]) {
						stale = false;
						break staleCheck;
					}
				}
			}
			if(stale) {
				clearInterval(drawCanvas);
				clearInterval(conway);
			}
			oboard = board;
		}
	}, updateTime);

	document.body.appendChild(canvas);
});
