async function sendMessage(message){

    const response = await fetch("/assistant",{

        method:"POST",

        headers:{
            "Content-Type":"application/json"
        },

        body:JSON.stringify({
            message:message
        })

    });

    return await response.json();

}