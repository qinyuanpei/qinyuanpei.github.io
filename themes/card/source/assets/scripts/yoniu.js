/* http://www.nmsl.wang */
	function h2c_(){
		var width = document.querySelector("#yoniu-poster").offsetWidth;
		var height = document.querySelector("#yoniu-poster").offsetHeight;
		var scale = 2;
		var canvas = document.createElement("canvas");
		var rect = document.querySelector("#yoniu-poster").getBoundingClientRect();
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
		html2canvas(document.querySelector("#yoniu-poster")).then(function(canvas) {
			var imgUrl = canvas.toDataURL("image/png", 1.0);
			var blob = base64Img2Blob(imgUrl);
			var aLink = document.querySelector("#yp-download");
			var evt = document.createEvent("HTMLEvents");
			aLink.download = new Date().getTime() + ".png";
			aLink.href = URL.createObjectURL(blob);
			aLink.innerHTML = "保存图片";
			aLink.target = "_blank";
			document.querySelector("#yp-load-yp").style = "display:none";
		});
	}
	function base64Img2Blob(code){
		var parts = code.split(';base64,');
		var contentType = parts[0].split(':')[1];
		var raw = window.atob(parts[1]);
		var rawLength = raw.length;

		var uInt8Array = new Uint8Array(rawLength);

		for (var i = 0; i < rawLength; ++i) {
		  uInt8Array[i] = raw.charCodeAt(i);
		}

		return new Blob([uInt8Array], {type: contentType});
	}