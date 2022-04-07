// CREATE TREE

function create_tree(container, frame, page, toolbar){

  var tree = document.createElement('div');
  //tree.type = 'tree';
  tree.frame = frame;
  if (page !== null)
    tree.nb_page = page.nb_page;
  tree.active_frame = frame;
  tree.help_msg = '';
  tree.toolbar = toolbar;

  tree.add_tree_data = function(tree_data, hide_root) {
    for (var j=0, lng=tree_data.length; j<lng; j++) {
      var arg = tree_data[j];
      var node_id=arg[0], parent_id=arg[1], text=arg[2], is_leaf=arg[3];
      tree.add_node(parent_id, node_id, is_leaf, text, (j===0));
      };
    tree.hide_root = hide_root;
    tree.write();
    };

  tree.add_toolbar_btn = function(toolbar, text, title) {
    var btn = document.createElement('div');
    toolbar.appendChild(btn);
    btn.style[cssFloat] = 'left';
    btn.tabIndex = -1  // remove from tab order
    btn.style.border = '1px solid darkgrey';
    btn.style.marginLeft = '5px';
    btn.style.marginRight = '5px';
    btn.style.marginTop = '5px';
    btn.style.paddingLeft = '5px';
    btn.style.paddingRight = '5px';
    btn.style.background = 'lightgrey';
    btn.style.position = 'relative';
    btn.innerHTML = text;
    btn.title = title;
    btn.onmouseover = function() {btn.style.cursor = 'default'};
    return btn;
    };

  tree.add_toolbar = function(container) {
    var toolbar = document.createElement('div');
    container.appendChild(toolbar);
    toolbar.style.margin = '10px 10px 5px 10px';
    toolbar.style.border = '1px solid lightgrey';
    toolbar.style.height = '28px';

    var app = tree.add_toolbar_btn(toolbar, 'Add', 'Append node (Insert)');
    app.onclick = function() {
      if (tree.frame.form.disable_count) return false;
      tree.req_append_node();
      tree.focus();
      };

    var ins = tree.add_toolbar_btn(toolbar, 'Ins', 'Insert node (Ctrl+Insert)');
    ins.onclick = function() {
      if (tree.frame.form.disable_count) return false;
      tree.req_insert_node();
      tree.focus();
      };

    var del = tree.add_toolbar_btn(toolbar, 'Del', 'Delete node (Ctrl+Delete)');
    del.onclick = function() {
      if (tree.frame.form.disable_count) return false;
      tree.req_delete_node();
      tree.focus();
      };

    var move = tree.add_toolbar_btn(toolbar, 'Move', 'Move node (Not implemented)');
    move.onclick = function() {
      if (tree.frame.form.disable_count) return false;
      tree.move_node();
      tree.focus();
      };
    };

  if (toolbar) {
    tree.add_toolbar(container);
    container.height -= 48;  // height + border + margins
    };
  container.appendChild(tree);

  tree.node_dict = {};
  tree.nodes = [];
  tree.tree = tree;
  tree.level = 0;
  tree.active_node = null;
  tree.has_focus = false;
  tree.allow_edit = false;  // can override

  tree.tabIndex = 0;  // so that it will accept 'focus'
  tree.style.outline = 'none';  // disable highlight on focus
  tree.style.height = container.height + 'px';
  tree.style.width = container.offsetWidth + 'px';
  tree.style.overflow = 'auto';

  tree.write = function() {
    while (this.childNodes.length)
      this.removeChild(this.firstChild);
    var root = this.nodes[0];
    if (this.hide_root)
      for (var i=0, l=root.nodes.length; i<l; i++)
        root.nodes[i].write(this);
    else
      root.write(this);
    };

  tree.onclick = function() {
    if (tree.frame.form.disable_count) return false;
    this.focus();
    };
  tree.onfocus = function() {
    this.has_focus = true;
    if (this.active_node === null) {
      if (this.hide_root)
        this.active_node = this.nodes[0].nodes[0];
      else
        this.active_node = this.nodes[0];
      this.onactive(this.active_node);
      };

    if (this.active_node.text_span !== undefined) {  // else returning from onblur()
      this.active_node.text_span.style.color = 'lightcyan';
      this.active_node.text_span.style.background = 'darkblue';
      };
    if (this.frame.ref !== null)  // i.e. not the menu
      got_focus(this);
    };
  tree.got_focus = function() {
    };
  tree.lost_focus = function() {
    return true;
    };
  tree.onblur = function() {
    this.has_focus = false;
    this.active_node.text_span.style.color = 'lightcyan';
    this.active_node.text_span.style.background = 'grey';
    };
//  return tree;
//  };

  tree.edit_label = function(active_node) {
    active_node.text_span.firstChild.style.display = 'none';
    var orig_value = active_node.text;
    var input = document.createElement('input');
    input.style.width = '80px';
    input.node = active_node;
    if (navigator.appName === 'Opera')
      input.onkeypress = input_handler;  // else 'return false' does not work
    else
      input.onkeydown = input_handler;
    input.onblur = function() {
      end_edit(this, false);
      };
    input.value = orig_value;
    active_node.style.height = '30px';
    active_node.text_span.appendChild(input);
    input.focus();
    };

  tree.input_handler = function(e) {
    if (e.key === 'Escape') {
      input = this;  // for setTimeout
      setTimeout(function() {end_edit(input, false);}, 0);
      return false;
      };
    if (e.key === 'Enter') {
      input = this;  // for setTimeout
      setTimeout(function() {end_edit(input, true);}, 0);
      return false;
      };
    };

  tree.end_edit = function(input, enter) {
    var node = input.node;
    var text_span = node.text_span;
    text_span.removeChild(text_span.childNodes[1]);
    text_span.firstChild.style.display = 'inline';
    if (navigator.appName === 'Opera')
      tree.onkeypress = key_handler;
    else
      tree.onkeydown = key_handler;
    if (enter) {
      node.text = input.value;
      node.text_node.nodeValue = input.value;
      };
    node.style.height = '21px';
    setTimeout(function() {tree.focus()}, 0);
    };

  tree.onkeydown = function(e) {
    switch (e.key) {
      case 'F2':  // edit text
        this.handle_edit(); return false; break;
      case 'ArrowLeft':
        this.handle_left(); return false; break;
      case 'ArrowRight':
        this.handle_right(); return false; break;
      case 'ArrowUp':
        this.handle_up(); return false; break;
      case 'ArrowDown':
        this.handle_down(); return false; break;
      case 'Enter':
        if (this.select_any || this.active_node.is_leaf) {
          //debug('enter ' + this.active_node.text + ' ' + this.active_node.node_id);
          node = this.active_node;
          setTimeout(function() {tree.onselected(node)}, 0);
          return false;
          };
        break;
      case 'Insert':
        if (this.toolbar) {
          if (e.ctrlKey) {
            if (tree.toolbar)
              this.req_insert_node();
            }
          else
            this.req_append_node();
          };
        return false; break;
      case 'Delete':
        if (this.toolbar)
          if (e.ctrlKey) {
            if (tree.toolbar)
              this.req_delete_node();
            };
        return false; break;
      case 'F3':
        if (this.toolbar)
          this.move_node();
        return false; break;
      };
    };

  tree.handle_edit = function() {
    if (!this.allow_edit)
      return;
    this.onkeydown = null;
    var active_node = this.active_node;
    setTimeout(function() {edit_label(active_node)}, 0);
    };

  tree.handle_left = function() {
    var active_node = this.active_node;
    if (active_node.expanded) {
      active_node.expanded = false;
      //this.active_node = active_node.parent;
      //var tree = this;  // to provide scope for setTimeout
      setTimeout(function() {tree.write()}, 0);
      }
    else {
      if ((active_node.level - this.hide_root) > 1) {
        active_node.text_span.style.color = this.style.color;
        active_node.text_span.style.background = this.style.background;
        active_node = active_node.parent;
        active_node.text_span.style.color = 'lightcyan';
        active_node.text_span.style.background = 'darkblue';
        this.active_node = active_node;
        this.onactive(active_node);
        };
      };
    };

  tree.handle_right = function() {
    var active_node = this.active_node;
    if (!active_node.is_leaf) {
      if (!active_node.expanded) {
        if (active_node.nodes.length) {
          active_node.expanded = true;
          this.active_node = active_node.nodes[0];
          this.onactive(this.active_node);
          //var tree = this;  // to provide scope for setTimeout
          setTimeout(function() {tree.write()}, 0);
          //tree.write();
          }
        else if (this.toolbar) {
          this.do_req_insert(active_node.node_id, 0);
          //var args = [this.ref, active_node.node_id, 0];
          //send_request('req_insert_node', args);
          };
        };
      };
    };

  tree.handle_up = function() {
    var active_node = this.active_node;
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
        if ((active_node.parent.level - this.hide_root) === 0)
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

    var node_top = active_node.getBoundingClientRect().top;
    var this_top = this.getBoundingClientRect().top;
    if (node_top < this_top)
      this.scrollTop -= active_node.offsetHeight;

    active_node.text_span.style.color = 'lightcyan';
    active_node.text_span.style.background = 'darkblue';
    this.active_node = active_node;
    this.onactive(active_node);
    };

  tree.handle_down = function() {
    var active_node = this.active_node;
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
      //if (active_node.parent.level === 0)
      //  break;  // parent is root
      if ((active_node.parent.level - this.hide_root) === 0)
        break;  // at top of tree
      active_node = active_node.parent;  // move up a level
      skip_expand = true;  // do not follow next expansion
      };
    if (orig_node != null)  // no ok node found - leave original
      active_node = orig_node;

    var node_bottom = active_node.getBoundingClientRect().bottom;
    var this_bottom = this.getBoundingClientRect().bottom;
    if (node_bottom > this_bottom)
      this.scrollTop += active_node.offsetHeight;

    active_node.text_span.style.color = 'lightcyan';
    active_node.text_span.style.background = 'darkblue';
    this.active_node = active_node;
    this.onactive(active_node);
    };

  tree.req_append_node = function() {
    var active_node = this.active_node;
    var parent = active_node.parent;
    if (parent === tree) {
      show_errmsg('Error', 'Cannot append to root');
      return;
      };
    this.do_req_insert(parent.node_id, parent.nodes.length);
    //var args = [this.ref, parent.node_id, parent.nodes.length];
    //send_request('req_insert_node', args);
    };

  tree.req_insert_node = function() {
    var active_node = this.active_node;
    var parent = active_node.parent;
    if (parent === tree) {
      show_errmsg('Error', 'Cannot insert into root');
      return;
      };
    var seq = parent.nodes.indexOf(active_node);
    this.do_req_insert(parent.node_id, seq);
    //var args = [this.ref, parent.node_id, seq];
    //send_request('req_insert_node', args);
    };

  tree.do_req_insert = function(node_id, seq) {
    if (this.combo === null || this.combo[2] === false) {
      var args = [this.ref, node_id, seq, null];
      send_request('req_insert_node', args);
      }
    else {
      this.req_args = [node_id, seq];
      var args = [null, 'Insert?', 'What do you want to insert?',
        [this.combo[0], this.combo[1], 'Cancel'], this.combo[0], 'Cancel', [this, this.send_req_insert]];
      ask_question(args);
      };
    };

  tree.send_req_insert = function(answer, node_id, seq) {
    // replace all 'tree.' with 'this.'  [2019-05-22]
    // it should work, as we have changed 'ask_question' to 'call' the callback
    // if tested successfully, remove this comment
    if (answer === 'Cancel')
      return;
    var node_id = this.req_args[0], seq = this.req_args[1];
    var combo_pos = this.combo.indexOf(answer);
    var combo_type = ['group', 'member'][combo_pos];
    var args = [this.ref, node_id, seq, combo_type];
    send_request('req_insert_node', args);
    };

  tree.req_delete_node = function() {
    if (this.active_node.parent === tree) {
      show_errmsg('Error', 'Cannot delete root node');
      return;
      };
    if (this.active_node.nodes.length) {
      show_errmsg('Error', 'Cannot delete a node with children');
      return;
      };
    var args = [null, 'Delete?', 'Sure you want to delete ' + this.active_node.text + '?',
      ['Yes', 'No'], 'No', 'No', tree.get_answer]
    ask_question(args);
    };

  tree.get_answer = function(answer) {
    if (answer === 'Yes') {
      var args = [tree.ref, tree.active_node.node_id];
      send_request('req_delete_node', args);
      };
    };

  tree.move_node = function() {
    debug3('move');
    // get node data from old position
    // insert node data into new position
    // delete old node
    // tree.write()
    };

  tree.insert_node = function(parent_id, seq, node_id) {
    var node = tree.add_node(parent_id, -1, false, '<new>', false, seq);
    if (!node.parent.expanded)
      node.parent.expanded = true;
    tree.active_node = node;
    tree.write();
    };

  tree.update_node = function(node_id, text, is_leaf) {
    var node = tree.active_node;
    if (node.node_id === -1) {
      node.node_id = node_id;
      tree.node_dict[node_id] = node;
      delete tree.node_dict[-1];
      };
    if (node_id !== node.node_id) {
      debug3('*** - node ' + node_id + ' is not the active node! - ***');
      return;
      };
    node.text = text;
    node.is_leaf = is_leaf;
    tree.write();
    };

  tree.delete_node = function(node_id) {
    var node = tree.active_node;
    if (node_id !== tree.active_node.node_id && node_id !== null) {
      debug3('*** - node ' + node_id + ' is not the active node! - ***');
      return;
      };
    var seq = node.parent.nodes.indexOf(node);
    for (var j=seq; j<node.parent.nodes.length; j++)
      node.parent.nodes[j].pos -= 1;
    node.parent.nodes.splice(seq, 1);
    delete tree.node_dict[node_id];
    if (seq < node.parent.nodes.length)
      tree.active_node = node.parent.nodes[seq]
    else if (node.parent.nodes.length)
      tree.active_node = node.parent.nodes[seq-1]
    else
      tree.active_node = node.parent;
    if (!tree.active_node.is_leaf)
      if (!tree.active_node.nodes.length)
        tree.active_node.expanded = false;
    tree.write();
    tree.active_node.text_span.style.color = 'lightcyan';
    tree.active_node.text_span.style.background = 'darkblue';
    this.onactive(tree.active_node);
    };

  tree.add_node = function(parent_id, node_id, is_leaf, text, is_root, seq){
    var node = document.createElement('div');
    if (is_root)
      var parent = tree;
    else
      var parent = tree.node_dict[parent_id];
    tree.node_dict[node_id] = node;
    node.parent = parent;
    node.node_id = node_id;
    node.is_leaf = is_leaf;  // 'branch' or 'leaf'
    node.text = text;
    node.nodes = [];
    node.expanded = false;
    node.level = parent.level + 1;
    if (seq === undefined) {
      node.pos = parent.nodes.length;
      parent.nodes.push(node);
      }
    else {
      for (var j=seq; j<parent.nodes.length; j++)
        parent.nodes[j].pos += 1;
      node.pos = seq;
      parent.nodes.splice(seq, 0, node);
      };

    node.style.height = '21px';
    node.style.border = '1px solid transparent';
    node.style.position = 'relative';

    node.write = function(tree) {
      tree.appendChild(node);

      while (node.childNodes.length)
        node.removeChild(node.firstChild);

      var node_span = document.createElement('span');
      node.appendChild(node_span);
      if (!node.is_leaf) {

        var canvas = document.createElement('div');
        canvas.style[cssFloat] = 'left';
        canvas.style.width = '15px';
        canvas.style.height = '15px';
        if (node.expanded)
          canvas.style.backgroundImage = 'url(' + iTreeOpen_src + ')';
        else
          canvas.style.backgroundImage = 'url(' + iTreeClosed_src + ')';
        canvas.style.position = 'relative';
        canvas.style.marginTop = '6px';
        canvas.style.marginLeft = ((node.level-1-tree.hide_root) * 25) + 5 + 'px';
        node_span.appendChild(canvas);
        canvas.node = node;

        var text_margin = 0;

        canvas.onclick = function() {
//          if (node.expanded)
//            tree.active_node = node.nodes[0];
//          else
//            tree.active_node = node;
//          node.expanded = !node.expanded;
//          setTimeout(function() {tree.write();}, 0);
          if (tree.frame.form.disable_count) return false;
          tree.active_node = node;
          if (node.expanded)
            tree.handle_left()
          else
            tree.handle_right();
          };
        }
      else
        var text_margin = ((node.level-1-tree.hide_root) * 25);

      var text_span = document.createElement('span');
      text_span.style.display = 'inline-block';
      text_span.style[cssFloat] = 'left';
      text_span.style.marginTop = '5px';
      text_span.style.marginLeft = text_margin + 5 + 'px';
      // to prevent selection of text - IE only
      text_span.onselectstart = function() {return false};
      var text = document.createTextNode(node.text);
      if (node === tree.active_node) {
        text_span.style.color = 'lightcyan';
        if (tree.has_focus)
          text_span.style.background = 'darkblue';
        else  // do we ever get here?
          text_span.style.background = 'grey';
        };
      text_span.onmouseover = function() {text_span.style.cursor = 'default'};
      text_span.onmouseleave = function() {text_span.style.cursor = 'default'};
      text_span.onclick = function() {
        if (tree.frame.form.disable_count) return false;
        tree.active_node.text_span.style.color = node.style.color;
        tree.active_node.text_span.style.background = node.style.background;
        node.text_span.style.color = 'lightcyan';
        node.text_span.style.background = 'darkblue';
        //if (!node.is_leaf) {
        //  if (!node.expanded) {
        //    node.expanded = true;
        //    tree.write();
        //    }
        //  }
        //else {
        if (tree.select_any || node.is_leaf)
          tree.onselected(node);
        if (node !== tree.active_node) {
          tree.active_node = node;
          tree.onactive(node);
          };
        };
      text_span.node = node;
      text_span.appendChild(text);
      node_span.appendChild(text_span);
      node.text_span = text_span;
      node.text_node = text;

      if (node.expanded)
        for (var i=0, l=node.nodes.length; i<l; i++)
          node.nodes[i].write(tree);
      };

    return node;
    };

  return tree;
  };

/*
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
*/

function create_tree_report(container, frame, page){

  var tree = document.createElement('div');
  //tree.type = 'tree';
  tree.frame = frame;
  if (page !== null)
    tree.nb_page = page.nb_page;
  tree.active_frame = frame;
  tree.help_msg = '';

  container.appendChild(tree);

  tree.node_dict = {};
  tree.nodes = [];
  tree.tree = tree;
  tree.level = 0;
  tree.active_node = null;
  tree.has_focus = false;

  tree.tabIndex = 0;  // so that it will accept 'focus'
  tree.style.outline = 'none';  // disable highlight on focus
  tree.style.height = container.height + 'px';
  tree.style.width = container.offsetWidth + 'px';
  tree.style.overflow = 'auto';

  tree.add_tree_data = function(tree_data, hide_root) {
    for (var j=0, lng=tree_data.length; j<lng; j++) {
      var arg = tree_data[j];
      var node_id=arg[0], parent_id=arg[1], text=arg[2], amount=arg[3], is_leaf=arg[4];
      tree.add_node(parent_id, node_id, is_leaf, text, amount);
      };
    tree.hide_root = hide_root;
    tree.write();
    };

  tree.write = function() {
    while (this.childNodes.length)
      this.removeChild(this.firstChild);
    var root = this.nodes[0];
    if (this.hide_root)
      for (var i=0, l=root.nodes.length; i<l; i++)
        root.nodes[i].write(this);
    else
      root.write(this);
    };

  tree.onclick = function() {
    if (tree.frame.form.disable_count) return false;
    this.focus();
    };
  tree.onfocus = function() {
    this.has_focus = true;
    if (this.active_node === null) {
      if (this.hide_root)
        this.active_node = this.nodes[0].nodes[0];
      else
        this.active_node = this.nodes[0];
      this.onactive(this.active_node);
      };

    if (this.active_node.text_span !== undefined) {  // else returning from onblur()
      this.active_node.text_span.style.color = 'lightcyan';
      this.active_node.text_span.style.background = 'darkblue';
      };
    if (this.frame !== null)  // i.e. not the menu
      got_focus(this);
    };
  tree.got_focus = function() {
    };
  tree.lost_focus = function() {
    return true;
    };
  tree.onblur = function() {
    this.has_focus = false;
    this.active_node.text_span.style.color = 'lightcyan';
    this.active_node.text_span.style.background = 'grey';
    };

  tree.key_handler = function(e) {
    if (!e) e=window.event;
    switch (e.key) {
      case 'ArrowLeft':
        this.handle_left(); return false; break;
      case 'ArrowRight':
        this.handle_right(); return false; break;
      case 'ArrowUp':
        this.handle_up(); return false; break;
      case 'ArrowDown':
        this.handle_down(); return false; break;
      };
    };

  if (navigator.appName === 'Opera')
    tree.onkeypress = tree.key_handler;  // else 'return false' does not work
  else
    tree.onkeydown = tree.key_handler;

  tree.handle_left = function() {
    var active_node = this.active_node;
    if (active_node.expanded) {
      active_node.expanded = false;
      //this.active_node = active_node.parent;
      //var tree = this;  // to provide scope for setTimeout
      setTimeout(function() {tree.write()}, 0);
      }
    else {
      if ((active_node.level - this.hide_root) > 1) {
        active_node.text_span.style.color = this.style.color;
        active_node.text_span.style.background = this.style.background;
        active_node = active_node.parent;
        active_node.text_span.style.color = 'lightcyan';
        active_node.text_span.style.background = 'darkblue';
        this.active_node = active_node;
        this.onactive(active_node);
        };
      };
    };

  tree.handle_right = function() {
    var active_node = this.active_node;
    if (!active_node.is_leaf) {
      if (!active_node.expanded) {
        if (active_node.nodes.length) {
          active_node.expanded = true;
          this.active_node = active_node.nodes[0];
          this.onactive(this.active_node);
          //var tree = this;  // to provide scope for setTimeout
          setTimeout(function() {tree.write()}, 0);
          //tree.write();
          }
        else {
          //this.do_req_insert(active_node.node_id, 0);
          var args = [this.ref, active_node.node_id, active_node.amount];
          send_request('req_insert_node', args);
          active_node.expanded = true;
          };
        };
      };
    };

  tree.handle_up = function() {
    var active_node = this.active_node;
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
        if ((active_node.parent.level - this.hide_root) === 0)
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

    var node_top = active_node.getBoundingClientRect().top;
    var this_top = this.getBoundingClientRect().top;
    if (node_top < this_top)
      this.scrollTop -= active_node.offsetHeight;

    active_node.text_span.style.color = 'lightcyan';
    active_node.text_span.style.background = 'darkblue';
    this.active_node = active_node;
    this.onactive(active_node);
    };

  tree.handle_down = function() {
    var active_node = this.active_node;
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
      //if (active_node.parent.level === 0)
      //  break;  // parent is root
      if ((active_node.parent.level - this.hide_root) === 0)
        break;  // at top of tree
      active_node = active_node.parent;  // move up a level
      skip_expand = true;  // do not follow next expansion
      };
    if (orig_node != null)  // no ok node found - leave original
      active_node = orig_node;

    var node_bottom = active_node.getBoundingClientRect().bottom;
    var this_bottom = this.getBoundingClientRect().bottom;
    if (node_bottom > this_bottom)
      this.scrollTop += active_node.offsetHeight;

    active_node.text_span.style.color = 'lightcyan';
    active_node.text_span.style.background = 'darkblue';
    this.active_node = active_node;
    this.onactive(active_node);
    };

  tree.add_node = function(parent_id, node_id, is_leaf, text, amount, seq){
    var node = document.createElement('div');
    if (tree.nodes.length === 0)
      var parent = tree;
    else
      var parent = tree.node_dict[parent_id];
    tree.node_dict[node_id] = node;
    node.parent = parent;
    node.node_id = node_id;
    node.is_leaf = is_leaf;  // 'branch' or 'leaf'
    node.text = text;
    node.amount = amount;
    node.nodes = [];
    node.expanded = false;
    node.level = parent.level + 1;
    if (seq === undefined) {
      node.pos = parent.nodes.length;
      parent.nodes.push(node);
      }
    else {
      for (var j=seq; j<parent.nodes.length; j++)
        parent.nodes[j].pos += 1;
      node.pos = seq;
      parent.nodes.splice(seq, 0, node);
      };

    node.style.height = '21px';
    node.style.border = '1px solid transparent';
    node.style.position = 'relative';

    node.write = function(tree) {
      tree.appendChild(node);

      while (node.childNodes.length)
        node.removeChild(node.firstChild);

      var node_span = document.createElement('span');
      node.appendChild(node_span);
      if (!node.is_leaf) {

        var canvas = document.createElement('div');
        canvas.style[cssFloat] = 'left';
        canvas.style.width = '15px';
        canvas.style.height = '15px';
        if (node.expanded)
          canvas.style.backgroundImage = 'url(' + iTreeOpen_src + ')';
        else
          canvas.style.backgroundImage = 'url(' + iTreeClosed_src + ')';
        canvas.style.position = 'relative';
        canvas.style.marginTop = '6px';
        canvas.style.marginLeft = ((node.level-1-tree.hide_root) * 25) + 5 + 'px';
        node_span.appendChild(canvas);
        canvas.node = node;

        var text_margin = 0;

        canvas.onclick = function() {
//          if (node.expanded)
//            tree.active_node = node.nodes[0];
//          else
//            tree.active_node = node;
//          node.expanded = !node.expanded;
//          setTimeout(function() {tree.write();}, 0);
          if (tree.frame.form.disable_count) return false;
          tree.active_node = node;
          if (node.expanded)
            tree.handle_left()
          else
            tree.handle_right();
          };
        }
      else
        var text_margin = ((node.level-1-tree.hide_root) * 25);

      var text_span = document.createElement('span');
      text_span.style.display = 'inline-block';
      text_span.style[cssFloat] = 'left';
      text_span.style.marginTop = '5px';
      text_span.style.marginLeft = text_margin + 5 + 'px';
      // to prevent selection of text - IE only
      text_span.onselectstart = function() {return false};
//      var text = document.createTextNode(node.text + ': ' + node.amount);

      var txt_span = document.createElement('span');
      txt_span.style.display = 'inline-block';
      txt_span.style.width = '80px';
      txt_span.style.textAlign = 'left';
      var txt_text = document.createTextNode(node.text);
      txt_span.appendChild(txt_text);
      text_span.appendChild(txt_span);

      var amt_span = document.createElement('span');
      amt_span.style.display = 'inline-block';
      amt_span.style.width = '100px';
      amt_span.style.textAlign = 'right';
      var amt_text = document.createTextNode(node.amount);
      amt_span.appendChild(amt_text);
      text_span.appendChild(amt_span);

      if (node === tree.active_node) {
        text_span.style.color = 'lightcyan';
        if (tree.has_focus)
          text_span.style.background = 'darkblue';
        else  // do we ever get here?
          text_span.style.background = 'grey';
        };
      text_span.onmouseover = function() {text_span.style.cursor = 'default'};
      text_span.onmouseleave = function() {text_span.style.cursor = 'default'};
      text_span.onclick = function() {
        if (tree.frame.form.disable_count) return false;
        tree.active_node.text_span.style.color = node.style.color;
        tree.active_node.text_span.style.background = node.style.background;
        node.text_span.style.color = 'lightcyan';
        node.text_span.style.background = 'darkblue';
        //if (!node.is_leaf) {
        //  if (!node.expanded) {
        //    node.expanded = true;
        //    tree.write();
        //    }
        //  }
        //else {
        if (tree.select_any || node.is_leaf)
          tree.onselected(node);
        if (node !== tree.active_node) {
          tree.active_node = node;
          tree.onactive(node);
          };
        };
      text_span.node = node;
//      text_span.appendChild(text);
      node_span.appendChild(text_span);
      node.text_span = text_span;
      node.text_node = text;

      if (node.expanded)
        for (var i=0, l=node.nodes.length; i<l; i++)
          node.nodes[i].write(tree);
      };

  tree.update_node = function(node_id, text, is_leaf) {
    var node = tree.active_node;
    if (node.node_id === -1) {
      node.node_id = node_id;
      tree.node_dict[node_id] = node;
      delete tree.node_dict[-1];
      };
    if (node_id !== tree.active_node.node_id) {
      debug3('*** - node ' + node_id + ' is not the active node! - ***');
      return;
      };
    node.text = text;
    node.is_leaf = is_leaf;
    tree.write();
    };

    return node;
    };

  return tree;
  };
