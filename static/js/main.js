var do_request = function(url,callback,method,data) {
	function reqListener () {
		callback.call(null,null,JSON.parse(this.responseText));
	};
	 
	var oReq = new XMLHttpRequest();
	oReq.onload = reqListener;
	oReq.onerror = function(err) {
		callback.call(null,err);
	}
	oReq.open(method || "get", url, true);
	if (method) {
		oReq.setRequestHeader("Content-Type", "application/json");
	}
	oReq.send(data);
};

var set_pages = function(pages,root) {
	while (root.firstChild) {
		root.removeChild(root.firstChild);
	}
	for (var page in pages) {
		var page_el = document.createElement('div');
		page_el.setAttribute('id','page_'+page);
		page_el.className = 'document_box';
		page_el.page = page;
		pages[page].pages.forEach(function(subpage) {
			var container_el = document.createElement('div');			
			container_el.className = 'page_box';
			var img_el = document.createElement('img');
			img_el.setAttribute('src','/thumbnails/'+subpage);
			container_el.appendChild(img_el);
			page_el.appendChild(container_el);
			img_el.page = subpage;
			img_el.setAttribute('draggable','true');
			img_el.addEventListener('dragstart', function (e) {
				e.dataTransfer.effectAllowed = 'copy';
				e.dataTransfer.setData('Text', this.page);
		    });
		    var deleter = document.createElement('div');
		    container_el.appendChild(deleter);
		    deleter.textContent = '✖';
		    deleter.className = 'remove_button';
		    deleter.addEventListener('click',function() {
		    	remove_page(img_el.page,page_el.page);
		    });
		});
		root.appendChild(page_el);
	  	page_el.addEventListener('dragover', function (e) {
		    if (e.preventDefault) {
		    	e.preventDefault();
		    }
		});
	  	page_el.addEventListener('drop', function (e) {
		    if (e.stopPropagation) {
		    	e.stopPropagation();
		    }
		    if (e.preventDefault) {
		    	e.preventDefault();
		    }
		    move_page(e.dataTransfer.getData('Text'),this.page);
		});
	}
}
var reload_pages = function() {
	do_request("/pages",function(err,pages) { set_pages(pages,document.getElementById('root')); });
};

var remove_page = function(page,parent) {
	do_request("/pages/"+parent,reload_pages,"delete",JSON.stringify([page]));
}

var move_page = function(page,new_parent) {
	do_request("/pages/"+new_parent,reload_pages,"post",JSON.stringify([page]));
};


reload_pages();