async function delete_order_element( element ) {
     
    var row = element.parentElement.parentElement;
    var order_id = parseInt(element.dataset.order_id);
    const response = await fetch("/api/order/check/?order_id=" + order_id);
    
    if (response.status == 200){
        const responsejson = await response.json();
        editable = responsejson['editable'];
        if (editable){
            row.remove();
            deleteElement(element, order_id);
            resizeOrderList();
        }
        else{
            orderTableDelete();
        }
        orderTotalAdjust(); 
    }
}

async function deleteElement(element, order_id) {
    try {
        const url = "/api/order/delete?id=" + element.dataset.phone_id.slice(3) + "&order_id=" + order_id;
        const csrftoken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
        const response = await fetch(url, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': csrftoken
            }
        });
        if (!response.ok) {
            throw new Error('Deleting error: ' + response.status);
        }

        if (response.status == 200){
            //const responseJson = await response.json();
            return "Delete element from order and DB success";
        }
        else {
            return ("Return from deleting element")
        }    
    } 
    catch (error) {
        console.error('Error in deleteElement:', error);
    }
}