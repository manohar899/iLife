function addUser()
{
    name = document.getElementById("selector").value;
    setValue = document.getElementById("names").value;
    if(setValue != "")
    setValue = setValue+','+name;
    else
        setValue = name;
    document.getElementById("names").innerHTML = setValue;
}
