var menuOpen = false;

document.addEventListener("DOMContentLoaded", e => {
	// MOBILE COMPATIBILITY

	const navbar = document.getElementById("navbar");
	const navitems = Array.from(navbar.children);

	if(navitems[0].offsetTop != navitems[navitems.length-1].offsetTop) {
		// Mobile device detected

		const mobileStyle = document.createElement("link");
		mobileStyle.rel = "stylesheet";
		mobileStyle.href = "$HOME/mobile.css";
		document.head.appendChild(mobileStyle);

		const menuButton = document.createElement("div");
		menuButton.classList.add("navitem");
		menuButton.innerHTML = "&lt;Menu&gt;";
		menuButton.style.fontStyle = "italic";

		navitems.forEach(item => item.style.display = "none");
		document.getElementById("navbar").appendChild(menuButton);

		menuButton.addEventListener("mouseup", e => {
			if(menuOpen) {
				menuOpen = false;
				navitems.forEach(item => item.style.display = "none");
				menuButton.innerHTML = "&lt;Menu&gt;";
				navbar.style.backgroundColor = "transparent";
			} else {
				menuOpen = true;
				navitems.forEach(item => item.style.display = "inline-block");
				menuButton.innerHTML = "&lt;Close Menu&gt;";
				navbar.style.backgroundColor = "#000000aa";
			}
		});
	}
});
