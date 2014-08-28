// CREATE TREE

function create_tree(container){
  var tree = document.createElement('div');
  tree.type = 'tree';
  container.appendChild(tree);

  tree.nodes = [];
  tree.tree = tree;
  tree.level = 0;
  tree.active_node = null;
  tree.has_focus = false;
  tree.allow_edit = false;  // can override

  tree.tabIndex = 0;  // so that it will accept 'focus'
  tree.style.outline = '0px solid transparent';
  if (navigator.appName === 'Opera')
    tree.onkeypress = key_handler;  // else 'return false' does not work
  else
    tree.onkeydown = key_handler;

  tree.write = function() {
    while (this.childNodes.length)
      this.removeChild(this.childNodes[0]);
    for (var i=0; i<this.nodes.length; i++)
      this.nodes[i].write(this);
    };

  tree.onclick = function(e) {
    if (!e) e=window.event;
    this.focus();
    };
  tree.onfocus = function(e) {
    if (!e) e=window.event;
    this.has_focus = true;
    this.active_node.text_span.style.color = 'lightcyan';
    this.active_node.text_span.style.background = 'darkblue';
    };
  tree.onblur = function(e) {
    if (!e) e=window.event;
    this.has_focus = false;
    this.active_node.text_span.style.color = 'lightcyan';
    this.active_node.text_span.style.background = 'grey';
    };
  return tree;
  };

edit_label = function(active_node) {
  active_node.text_span.firstChild.style.display = 'none';
  var orig_value = active_node.text;
  var input = document.createElement('input');
  input.style.width = '80px';
  input.node = active_node;
  if (navigator.appName === 'Opera')
    input.onkeypress = input_handler;  // else 'return false' does not work
  else
    input.onkeydown = input_handler;
  input.onblur = function(e) {
    if (!e) e=window.event;
    end_edit(this, false);
    };
  input.value = orig_value;
  active_node.style.height = '30px';
  active_node.text_span.appendChild(input);
  input.focus();
  };

input_handler = function(e) {
  if (!e) e=window.event;
  if (e.keyCode === 27) {
    input = this;  // for setTimeout
    setTimeout(function() {end_edit(input, false);}, 0);
    return false;
    };
  if (e.keyCode === 13) {
    input = this;  // for setTimeout
    setTimeout(function() {end_edit(input, true);}, 0);
    return false;
    };
  };

end_edit = function(input, enter) {
  var node = input.node;
  var text_span = node.text_span;
  text_span.removeChild(text_span.childNodes[1]);
  text_span.firstChild.style.display = 'inline';
  if (navigator.appName === 'Opera')
    node.tree.onkeypress = key_handler;
  else
    node.tree.onkeydown = key_handler;
  if (enter) {
    node.text = input.value;
    node.text_node.nodeValue = input.value;
    };
  node.style.height = '21px';
  tree = node.tree;
  setTimeout(function() {tree.focus()}, 0);
  };

key_handler = function(e) {
  if (!e) e=window.event;
  //debug(e.keyCode);
  if (e.keyCode === 113) { // F2 - edit text
    if (!this.allow_edit)
      return false;
    if (navigator.appName === 'Opera')
      this.onkeypress = null;
    else
      this.onkeydown = null;
    active_node = this.active_node;
    setTimeout(function() {edit_label(active_node)}, 0);
    return false;
    };

  if (e.keyCode === 37) {  // left
    active_node = this.active_node;
    if (active_node.expanded) {
      active_node.expanded = false;
      //this.active_node = active_node.parent;
      var tree = this;  // to provide scope for setTimeout
      setTimeout(function() {tree.write()}, 0);
      }
    else
      if (active_node.level > 1) {
        active_node.text_span.style.color = this.style.color;
        active_node.text_span.style.background = this.style.background;
        active_node = active_node.parent;
        active_node.text_span.style.color = 'lightcyan';
        active_node.text_span.style.background = 'darkblue';
        this.active_node = active_node;
        };
    return false;
    };

  if (e.keyCode === 39) {  // right
    active_node = this.active_node;
    if (active_node.expandable)
      if (!active_node.expanded) {
        active_node.expanded = true;
        this.active_node = active_node.nodes[0];
        var tree = this;  // to provide scope for setTimeout
        setTimeout(function() {tree.write()}, 0);
        };
    return false;
    };

  if (e.keyCode === 38) {  // up
    active_node = this.active_node;
    active_node.text_span.style.color = this.style.color;
    active_node.text_span.style.background = this.style.background;

    var check_expand = false;
    var orig_node = active_node;
    while (true) {
      if (check_expand)
        if (active_node.expanded) {
          active_node = active_node.nodes[active_node.nodes.length-1];
          continue;
          }
        else {
          orig_node = null;  // new node is ok
          break;
          };
      if (active_node.pos > 0)
        if (!active_node.parent.nodes[active_node.pos-1].expanded)
          {
          active_node = active_node.parent.nodes[active_node.pos-1];
          orig_node = null;  // new node is ok
          break;
          };
      if (active_node.pos === 0)
        if (active_node.parent.level === 0)
          break;  // at top of tree
      else {
        active_node = active_node.parent;
        orig_node = null;  // new node is ok
        break;
        };
      active_node = active_node.parent.nodes[active_node.pos-1];
      check_expand = true;
      };
    if (orig_node != null)  // no ok node found - leave original
      active_node = orig_node;

    active_node.text_span.style.color = 'lightcyan';
    active_node.text_span.style.background = 'darkblue';
    this.active_node = active_node;
    return;  //false;
    };

  if (e.keyCode === 40) {  // down
    active_node = this.active_node;
    active_node.text_span.style.color = this.style.color;
    active_node.text_span.style.background = this.style.background;

    var skip_expand = false;
    var orig_node = active_node;
    while (true) {
      if (active_node.nodes.length)
        if (active_node.expanded)
          if (!skip_expand) {
            active_node = active_node.nodes[0];
            orig_node = null;  // new node is ok
            break;
            };
      if (active_node.pos < (active_node.parent.nodes.length-1)) {
        active_node = active_node.parent.nodes[active_node.pos+1];
        orig_node = null;  // new node is ok
        break;
        };
      if (active_node.parent.level === 0) {
        break;  // parent is root
        };
      active_node = active_node.parent;  // move up a level
      skip_expand = true;  // do not follow next expansion
      };
    if (orig_node != null)  // no ok node found - leave original
      active_node = orig_node;

    active_node.text_span.style.color = 'lightcyan';
    active_node.text_span.style.background = 'darkblue';
    this.active_node = active_node;
    return;  //false;
    };

  if (e.keyCode === 13)  // enter
    if (!this.active_node.expandable) {
      //debug('enter ' + this.active_node.text + ' ' + this.active_node.node_id);
      node = this.active_node;
      setTimeout(function() {node.onselected()}, 0);
      return false;
      };

  if (e.keyCode === 45)  // insert
    if (e.ctrlKey) {
      debug('ctrl insert');
      return false;
      };

  if (e.keyCode === 46)  // delete
    if (e.ctrlKey) {
      debug('ctrl delete');
      return false;
      };
  };

// ADD NODE

function add_node(parent, node_id, expandable, text){
  var node = document.createElement('div');

  node.parent = parent;
  node.node_id = node_id;
  node.expandable = expandable;  // 'branch' or 'leaf'
  node.text = text;
  node.tree = parent.tree;
  node.nodes = [];
  node.expanded = false;
  node.level = parent.level + 1;
  node.pos = parent.nodes.length;
  parent.nodes[parent.nodes.length] = node;
  if (node.tree.active_node === null)
    node.tree.active_node = node;

  node.style.height = '21px';
  node.style.border = '1px solid transparent';
  node.style.position = 'relative';

  node.write = function(tree) {
    tree.appendChild(this);

    while (this.childNodes.length)
      this.removeChild(this.childNodes[0]);

    var node_span = document.createElement('span');
    node_span.style.display = 'inline-block';
    this.appendChild(node_span);
    if (this.expandable) {

      var canvas = document.createElement('div');
      canvas.style[cssFloat] = 'left';
//      canvas.style.width = '12px';
//      canvas.style.height = '12px';
//      canvas.style.margin = '1px 2px 1px 1px';
//      //canvas.style.background = 'lightgrey';
      canvas.style.width = '15px';
      canvas.style.height = '15px';
      if (this.expanded)
        canvas.style.backgroundImage = 'url(' + iTreeOpen_src + ')';
      else
        canvas.style.backgroundImage = 'url(' + iTreeClosed_src + ')';
//      canvas.style.borderTop = '1px solid white';
//      canvas.style.borderLeft = '1px solid white';
//      canvas.style.borderRight = '1px solid black';
//      canvas.style.borderBottom = '1px solid black';
      canvas.style.position = 'relative';
      canvas.style.marginTop = '6px';
      canvas.style.marginLeft = ((this.level-1) * 25) + 5 + 'px';
      node_span.appendChild(canvas);
      canvas.node = this;

//      var canvas = new_canvas(15, 15, node_span);
//      canvas.node = this;
//      if (this.expanded)
//        draw_open(canvas, 4, 4);
//      else
//        draw_closed(canvas, 4, 4);
//      canvas.style.marginTop = '6px';
//      canvas.style.marginLeft = ((this.level-1) * 25) + 5 + 'px';

      var text_margin = 0;

      canvas.onclick = function(e) {
        var node = this.node;
        //if (!node.expanded && node.nodes.length === 0)
        //  node.get_children();  // not used at present - all children exist
        if (node.expanded)
          node.tree.active_node = node.nodes[0];
        else
          node.tree.active_node = node;
        node.expanded = !node.expanded;
        var tree = node.tree;  // to provide scope for setTimeout
        setTimeout(function() {tree.write();}, 0);
        };
      }
    else
      var text_margin = ((this.level-1) * 25);

//    var text_div = document.createElement('div');
//    this.appendChild(text_div);

//    this.text_div = text_div;
//    text_div.node = this;
//    text_div.style.marginTop = '5px';
//    text_div.style.marginLeft = text_margin + 5 + 'px';
//    // to prevent selection of text - IE only
//    text_div.onselectstart =
//      function(){return false};
//    var text_span = document.createElement('span');
//    text_div.appendChild(text_span);
//    text_div.onclick = function(e) {
//      if (!e) e=window.event;
//      // to prevent selection of text - W3C only
//      if (e.preventDefault) {e.preventDefault()};
//      tree = this.parentNode.parentNode.tree;
//      if (tree.active_node != this.node) {
//        tree.active_node.text_div.style.color = tree.style.color;
//        tree.active_node.text_div.style.background = tree.style.background;
//        tree.active_node = this.node;
//        this.style.color = 'lightcyan';
//        this.style.background = 'darkblue';
//        };
//      };
//    text_div.ondblclick = function(e) {
//      if (!e) e=window.event;
//      tree = this.parentNode.parentNode.tree;
//      if (tree.active_node != this.node) {
//        tree.active_node.text_div.style.color = tree.style.color;
//        tree.active_node.text_div.style.background = tree.style.background;
//        tree.active_node = this.node;
//        this.style.color = 'lightcyan';
//        this.style.background = 'darkblue';
//        };
//      node = this.node;
//      setTimeout(function() {node.onselected()}, 0);
//      };
//    text_span.style.cursor = 'default';

    var text_span = document.createElement('span');
    text_span.style.display = 'inline-block';
    text_span.style.marginTop = '5px';
    text_span.style.marginLeft = text_margin + 5 + 'px';
    // to prevent selection of text - IE only
    text_span.onselectstart =
      function(){return false};
    var text = document.createTextNode(this.text);
    if (this.tree.active_node === this) {
      text_span.style.color = 'lightcyan';
      if (this.tree.has_focus)
        text_span.style.background = 'darkblue';
      else  // do we ever get here?
        text_span.style.background = 'grey';
      };
    text_span.onmouseover = function() {text_span.style.cursor = 'default'};
    text_span.onmouseleave = function() {text_span.style.cursor = 'default'};
    text_span.onclick = function(e) {
      var node = this.node;
      active_node = node.tree.active_node;
      active_node.text_span.style.color = this.style.color;
      active_node.text_span.style.background = this.style.background;
      this.style.color = 'lightcyan';
      this.style.background = 'darkblue';
      node.tree.active_node = node;
      if (node.expandable) {
        if (!node.expanded) {
          node.expanded = true;
          //var tree = node.tree;  // to provide scope for setTimeout
          //setTimeout(function() {tree.write();}, 0);
          node.tree.write();
          }
        }
      else {
        //setTimeout(function() {node.onselected()}, 0);
        node.onselected();
        };
      };
    text_span.node = this;
    text_span.appendChild(text);
    node_span.appendChild(text_span);
    this.text_span = text_span;
    this.text_node = text;

    if (this.expanded) {
      for (var i=0;i<this.nodes.length;i++)
        this.nodes[i].write(tree);
      };
    };

  return node;
  };

function draw_open(canvas, x, y) {
  var ctx = canvas.getContext('2d');
  ctx.beginPath();
  ctx.strokeStyle = "silver";
  ctx.strokeRect(x-0.5, y-0.5, 8, 8);
  ctx.strokeStyle = "black";
  ctx.moveTo(x+1.5, y+3.5);
  ctx.lineTo(x+5.5, y+3.5);
  ctx.stroke()
  };

function draw_closed(canvas, x, y) {
  var ctx = canvas.getContext('2d');
  ctx.beginPath();
  ctx.strokeStyle = "silver";
  ctx.strokeRect(x-0.5, y-0.5, 8, 8);
  ctx.strokeStyle = "black";
  ctx.moveTo(x+1.5, y+3.5);
  ctx.lineTo(x+5.5, y+3.5);
  ctx.moveTo(x+3.5, y+1.5);
  ctx.lineTo(x+3.5, y+5.5);
  ctx.stroke()
  };
