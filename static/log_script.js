const input = document.getElementById("log-password");

const check = document.getElementById("check");
let pass_status = false;

check.addEventListener("change", () => {
    if (pass_status)
    {
        pass_status = false;
        input.type = "password";
    }
    else
    {
        pass_status = true;
        input.type = "text";
    }
});

const input2 = document.getElementById("password2");

const check2 = document.getElementById("check2");
let pass_status2 = false;

check2.addEventListener("change", () => {
    if (pass_status2)
    {
        pass_status2 = false;
        input2.type = "password";
    }
    else
    {
        pass_status2 = true;
        input2.type = "text";
    }
});