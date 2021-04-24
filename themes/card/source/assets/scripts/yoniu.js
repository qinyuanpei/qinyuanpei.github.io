/* http://www.nmsl.wang */
function h2c_() {
	var width = document.getElementById("yoniu-poster").offsetWidth;
	var height = document.getElementById("yoniu-poster").offsetHeight;
	var scale = 2;
	var canvas = document.createElement("canvas");
	var rect = document.getElementById("yoniu-poster").getBoundingClientRect();
	canvas.width = width * scale;
	canvas.height = height * scale;
	var context = canvas.getContext("2d");
	context.scale(scale, scale);
	context.translate(-rect.left, -rect.top);
	var options = {
		scale: scale,
		canvas: canvas,
		width: width,
		height: height,
		taintTest: true,
		useCORS: true,
		dpi: window.devicePixelRatio,
	};
	html2canvas(document.getElementById("yoniu-poster")).then(function (canvas) {
		var imgUrl = canvas.toDataURL("image/png", 1.0);
		var blob = base64Img2Blob(imgUrl);
		var aLink = document.getElementById("yp-download");
		var evt = document.createEvent("HTMLEvents");
		aLink.download = new Date().getTime() + ".png";
		aLink.href = URL.createObjectURL(blob);
		aLink.innerHTML = "保存图片";
		aLink.target = "_blank";
		document.getElementById("yp-load-yp").style = "display:none";
	});
}
function base64Img2Blob(code) {
	var parts = code.split(';base64,');
	var contentType = parts[0].split(':')[1];
	var raw = window.atob(parts[1]);
	var rawLength = raw.length;

	var uInt8Array = new Uint8Array(rawLength);

	for (var i = 0; i < rawLength; ++i) {
		uInt8Array[i] = raw.charCodeAt(i);
	}

	try {
		var blob = new Blob([uInt8Array], { type: contentType });
		return blob;
	}
	catch (e) {
		// TypeError old chrome and FF
		window.BlobBuilder = window.BlobBuilder ||
			window.WebKitBlobBuilder ||
			window.MozBlobBuilder ||
			window.MSBlobBuilder;
		if (e.name == 'TypeError' && window.BlobBuilder) {
			var bb = new BlobBuilder();
			bb.append([uInt8Array.buffer]);
			var jpeg = bb.getBlob(contentType);
			return jpeg;
		}
		else if (e.name == "InvalidStateError") {
			// InvalidStateError (tested on FF13 WinXP)
			var jpeg = new Blob([uInt8Array.buffer], { type: contentType });
			return jpeg;
		}
		else {
			// We're screwed, blob constructor unsupported entirely
		}
	}
}