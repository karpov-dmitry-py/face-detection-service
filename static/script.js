const canvas=document.getElementById('canvas');
const img=document.getElementById('actual-image');
const detected_items = [];
const y_canvas_offset = document.querySelector('.header').scrollHeight;

function drawFaces (items) {
    const ctx=canvas.getContext("2d");
    ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
    ctx.strokeStyle="cyan";
    ctx.lineWidth = 8;

    items.forEach(function(item) {
        ctx.strokeRect(item.x, item.y, item.width, item.height);
    });
    console.log(items);
};

function removeFaces (items, x, y) {
    console.log(`clicked y = ${y}`);
    console.log(`clicked x = ${x}`);
    console.log(`y_canvas_offset = ${y_canvas_offset}`);
    y -= y_canvas_offset;
    console.log(`clicked y after y_canvas_offset = ${y}`)
    deleted_count = 0;
    for (let i = 0; i < items.length; i++) {
        current_index = i-deleted_count;
        item = items[current_index];
        if ((item.x <= x) && (item.y <= y) && ((item.x + item.width) >= x) && ((item.y + item.height) >= y)) {
            console.log(`item being removed = ${item.x}, ${item.y}, ${item.width}, ${item.height},
            item.x + item.width = ${item.x + item.width},
            item.y + item.height = ${item.y + item.height}`),

            items.splice(current_index, 1);
            deleted_count += 1;
            console.log(items);
        };
    };
    if (deleted_count != 0) {
        console.log(`deleted_count = ${deleted_count}`)
        drawFaces(items);
    };
}

window.onload = function() {
    const img=document.getElementById("actual-image");
    canvas.width = img.width;
    canvas.height = img.height;

    const detections = document.querySelectorAll('.detected-face-item');
    detections.forEach(function(item) {
        coords = item.innerText.split(',');
        const x = Number(coords[0]);
        const y = Number(coords[1]);
        const width = Number(coords[2]);
        const height = Number(coords[3]);

        // save items
        current_item = {
            id: item.id,
            x: x,
            y: y,
            width: width,
            height: height
        }
        detected_items.push(current_item);
    });
    drawFaces(detected_items);

};

//canvas.addEventListener('contextmenu', e => {
canvas.addEventListener('mouseup', e => {
//    console.clear();
//    console.log(e.pageX);
//    console.log(e.pageY);
//    console.log(e);
//    current_item = {
//        id: 100,
//        x: 100,
//        y: 200,
//        width: 150,
//        height: 150
//    }
//    detected_items.push(current_item)
//    detected_items.splice(0, 1);
    if (e.which == 3) {
        removeFaces(detected_items, e.pageX, e.pageY);
    }
});