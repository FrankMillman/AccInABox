menu = null;  // initialise - must be global
function start_menu(args) {
  var menu_obj = {};  //new Object();

  //debug3(JSON.stringify(args));

  var toolbar=false, hide_root=true;
  for (var i=0, l=args.length; i<l; i++) {
    var arg = args[i];
    var node_id=arg[0], parent_id=arg[1], text=arg[2], expandable=arg[3];
    if (i === 0)
      menu = create_tree(menu_div, null, toolbar, hide_root);
    menu.add_node(parent_id, node_id, expandable, text, (i===0));
    };
  menu.onselected = function(node) {
    var args = [node.node_id];
    send_request('menuitem_selected', args);
    };
  menu.onactive = function(node) {
    };
  menu.write();
  setTimeout(function() {menu.focus()}, 0);
  };
