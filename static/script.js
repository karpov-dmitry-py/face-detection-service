window.onload = function() {
    const canvas=document.getElementById("canvas");
    const ctx=canvas.getContext("2d");
    const img=document.getElementById("actual-image");
    ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
    ctx.strokeStyle="darkblue";
    ctx.strokeStyle.width = 10;
    ctx.lineWidth = 10;

    x_ratio = canvas.width / img.width
    y_ratio = canvas.height / img.height

    const detections = document.querySelectorAll('.detected-face-item');
    detections.forEach(function(item) {
        coords = item.innerText.split(',');
        ctx.strokeRect(coords[0]*x_ratio, coords[1]*y_ratio, coords[2]*x_ratio, coords[3]*y_ratio);
    });
};