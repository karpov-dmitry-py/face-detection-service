const canvas = document.getElementById('canvas');
const img = document.getElementById('actual-image');
const detected_items = [];
const y_canvas_offset = document.querySelector('.header').scrollHeight;
const arbitrarySelectionMinSize = 50;
let x_start_select = 0;
let x_end_select = 0;
let y_start_select = 0;
let y_end_select = 0;

function resetSelection() {
    let x_start_select = 0;
    let x_end_select = 0;
    let y_start_select = 0;
    let y_end_select = 0;
};

function drawFaces (items) {
    const ctx=canvas.getContext("2d");
    ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
    ctx.strokeStyle="cyan";
    ctx.lineWidth = 8;

    items.forEach(function(item) {
        ctx.strokeRect(item.x, item.y, item.width, item.height);
    });
};

function removeFaces (items, x, y) {
    y -= y_canvas_offset;
    deleted_count = 0;
    for (let i = 0; i < items.length; i++) {
        current_index = i-deleted_count;
        item = items[current_index];
        if ((item.x <= x) && (item.y <= y) && ((item.x + item.width) >= x) && ((item.y + item.height) >= y)) {
            items.splice(current_index, 1);
            deleted_count += 1;
        };
    };
    if (deleted_count > 0) {
        drawFaces(items);
    };
}

window.onload = function() {
    const img=document.getElementById('actual-image');
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

canvas.addEventListener('mousedown', e => {
    y_adjusted_start_select = e.pageY - y_canvas_offset;
    if (e.which == 1 && e.pageX <= canvas.width && y_adjusted_start_select <= canvas.height ) {
        x_start_select = e.pageX;
        y_start_select = y_adjusted_start_select;
    };
});

canvas.addEventListener('mouseup', e => {
    if (e.which == 3) {
        removeFaces(detected_items, e.pageX, e.pageY);
        return;
    }

    y_adjusted_end_select = e.pageY - y_canvas_offset;
    if (e.which == 1 && x_start_select != 0 && e.pageX <= canvas.width && y_adjusted_end_select <= canvas.height ) {
        x_end_select = e.pageX;
        y_end_select = y_adjusted_end_select;
        width = x_end_select - x_start_select;
        x_start = (width > 0) ? x_start_select : x_end_select;
        width = (width < 0) ? -width : width;
        if (width < arbitrarySelectionMinSize) {
            resetSelection();
            return;
        }

        height = y_end_select - y_start_select;
        y_start = (height > 0) ? y_start_select : y_end_select;
        height = (height < 0) ? -height : height;
        if (height < arbitrarySelectionMinSize) {
            resetSelection();
            return;
        }

        new_item = {
            id: detected_items.length+1,
            x: x_start,
            y: y_start,
            width: width,
            height: height
        }
        detected_items.push(new_item)
        drawFaces(detected_items);

        x_start_select = 0;
        x_end_select = 0;
        y_start_select = 0;
        y_end_select = 0;
    };

});

document.querySelector('.btn-update-image-data').addEventListener('click', updateImageData);
async function updateImageData (e) {
    let response = await fetch(window.location.href, {
        method: 'POST',
        headers: {
          Accept: 'application/json',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(detected_items)
      });
    const { status } = response;
    statusDiv = document.querySelector('#async-update-status')
    msg = status == 200 ? 'Image changes have been saved successfully!' : 'Could not save image changes!';
    statusDiv.hidden = false;
    statusDiv.innerText = msg;
};

