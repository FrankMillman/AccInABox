menu = null;  // initialise - must be global
function start_menu(args) {
  var toolbar=false, hide_root=true;

  if (menu_div.childNodes.length === 2)  // receiving updated menu
    menu_div.removeChild(menu_div.lastChild);  // remove existing menu first

  // next 4 lines set up tree.frame.form.disable_count, required by tree.js
  var form = {};
  form.disable_count = 0;
  var frame = {};
  frame.form = form;
  frame.ref = null;
  menu = create_tree(menu_div, frame, null, toolbar);
//  for (var i=0, l=args.length; i<l; i++) {
//    var arg = args[i];
//    var node_id=arg[0], parent_id=arg[1], text=arg[2], is_leaf=arg[3];
//    menu.add_node(parent_id, node_id, is_leaf, text, (i===0));
//    };
  menu.add_tree_data(args, hide_root);
  menu.onselected = function(node) {
    var args = [node.node_id];
    send_request('menuitem_selected', args);
    };
  menu.onactive = function(node) {
    };
  menu.write();
  setTimeout(function() {menu.focus()}, 0);
  };
