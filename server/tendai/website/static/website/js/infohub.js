/* Main infohub widget file. This file is required in addition
   to all individual widget files. */

infohub = {};
infohub.widget = {};

(function() {
    var widget = function() {
	var node = d3.select(this);
	var widget_type = node.attr('data-widget');
	console.log(widget_type);
	if (infohub.widget[widget_type]) {
	    var w = new infohub.widget[widget_type](node);
	}
    }
    
    window.onload = function() {
	var widgets = d3.selectAll('[data-source=infohub]')
	    .each(widget);
    }
})();