async function edit_order_element(element){
    if (vat.textContent === "Invalid"){
        element.parentElement.previousElementSibling.firstElementChild.value = '';
        alert('VAT not valid');
    };
    new_qty = element.parentElement.previousElementSibling.firstElementChild.value
    if(new_qty){
        var order_id = parseInt(element.dataset.order_id);
        const response = await fetch("/api/order/check/?order_id=" + order_id);
        
        if (response.status == 200){
            const responsejson = await response.json();
            editable = responsejson['editable'];
            if (editable){
                if (parseInt(new_qty, 10)!==0 ){
                    element.parentElement.previousElementSibling.previousElementSibling.previousElementSibling.textContent = new_qty
                    var price = element.dataset.price;
                    var new_price = (price * new_qty).toFixed(2)+'€';
                    element.parentElement.previousElementSibling.firstElementChild.value = "";
                    element.parentElement.previousElementSibling.previousElementSibling.textContent = new_price;
                    addElement(element, new_qty, order_id);
                    }
                else{
                    delete_order_element(element);
                    deleteElement(element);
                }
            }
            else{
                orderTableDelete();
                element.parentElement.previousElementSibling.firstElementChild.value = "";
            }
            orderTotalAdjust(); 
        }
    }

    else{
        var element = element.parentElement.previousElementSibling.firstElementChild;
        element.style.borderColor = "red";
        setTimeout( function (){
            element.style.borderColor = "";
        }, 1000);
    }
}

async function addElement(element, new_qty, order_id) {
    try {
        const url = "/api/order/update?id=" + element.dataset.phone_id.slice(3) + "&quantity=" + new_qty + "&order_id=" + order_id;
        const csrftoken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
        const response = await fetch(url, {
            method: 'PUT',
            headers: {
                'X-CSRFToken': csrftoken
            }
        });
        
        if (!response.ok) {
            throw new Error('Request error: ' + response.status);
        }
        const responseJson = await response.json();
        return "create";
    } 
    catch (error) {
        console.error('Error in addElement:', error);
    }
}