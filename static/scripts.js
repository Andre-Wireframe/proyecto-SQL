const nav_button = document.getElementById("nav-but");
const ul = document.getElementById("nav-ul");
const nav = document.querySelector("nav"); 

let nav_status = 0;
nav_button.addEventListener("click", () => {
    if (nav_status == 0)
    {
        ul.style.display = "flex";
        nav.style.height = "270px";
        nav_status = 1;
    }
    else
    {
        ul.style.display = "none";
        nav.style.height = "70px";
        nav_status = 0;
    }
});