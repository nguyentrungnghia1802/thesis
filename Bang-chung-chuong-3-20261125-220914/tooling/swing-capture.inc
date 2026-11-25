
    private static void layoutTree(Component component) {
        if (component instanceof Container container) {
            container.doLayout();
            for (Component child : container.getComponents()) if(child.isVisible()) layoutTree(child);
        }
    }

    private static void panelImage(Path file,JComponent panel,int width,int height) throws Exception {
        Dimension previous=panel.getSize();
        try {
            panel.setSize(width,height);
            layoutTree(panel);
            render(file,panel,width,height);
        } finally {
            panel.setSize(previous);
            layoutTree(panel);
        }
    }

    private static javax.swing.table.TableColumnModel visibleColumns(JTable table,int... indices) {
        var original=table.getColumnModel();
        var subset=new javax.swing.table.DefaultTableColumnModel();
        for(int i:indices)subset.addColumn(original.getColumn(i));
        table.setColumnModel(subset);
        return original;
    }

    private static void workbench(Path file,JPanel view,JSplitPane split,String active) throws Exception {
        onEdt(()->{
            var artifacts=(JTable)find(view,c->c instanceof JTable t&&t.isShowing()&&"Artifact".equals(t.getColumnName(0)));
            require(artifacts!=null,"Visible source artifacts");
            var right=(JTable)find(view,c->c instanceof JTable t&&t.isShowing()&&
                (active.equals("Checkpoints")?"Checkpoint".equals(t.getColumnName(0)):"Object".equals(t.getColumnName(0))));
            require(right!=null,"Visible evaluation table");
            boolean timeline=active.equals("Checkpoints");
            int divider=timeline?465:250;
            int selected=right.getSelectedRow();
            int oldDivider=split.getDividerLocation();
            Dimension old=view.getSize();
            int rowHeight=artifacts.getRowHeight();
            var left=visibleColumns(artifacts,0,2);
            var allRight=timeline?visibleColumns(right,0,1,2,3,5,6):visibleColumns(right,1,2,3,4);
            var properties=artifacts.getColumnModel().getColumn(1);
            var previousRenderer=properties.getCellRenderer();
            int defaultRightHeight=right.getRowHeight();
            var rightWidths=timeline?new int[]{85,65,225,136,110,129}:new int[]{200,165,184,75};
            try {
                artifacts.setRowHeight(timeline?58:23);
                right.setRowHeight(19);
                properties.setCellRenderer((table,value,isSelected,focus,row,col)->{
                    var label=new JTextArea(Objects.toString(value,""));
                    label.setFont(table.getFont());
                    label.setBorder(BorderFactory.createEmptyBorder(1,4,1,4));
                    label.setLineWrap(true);
                    label.setWrapStyleWord(true);
                    label.setBackground(isSelected?table.getSelectionBackground():table.getBackground());
                    label.setForeground(isSelected?table.getSelectionForeground():table.getForeground());
                    return label;
                });
                configure(artifacts,66,divider-81);
                configure(right,rightWidths);
                view.setSize(timeline?1250:930,timeline?318:248);
                split.setDividerLocation(divider);
                layoutTree(view);
                if(selected>=0) {
                    right.getSelectionModel().setSelectionInterval(selected,selected);
                    right.scrollRectToVisible(right.getCellRect(selected,0,true));
                }
                render(file,view,view.getWidth(),view.getHeight());
            } finally {
                artifacts.setColumnModel(left);
                properties.setCellRenderer(previousRenderer);
                right.setColumnModel(allRight);
                artifacts.setRowHeight(rowHeight);
                right.setRowHeight(defaultRightHeight);
                view.setSize(old);
                split.setDividerLocation(oldDivider);
                layoutTree(view);
            }
            return null;
        });
    }

    private static void markingView(Path base,Container view,String key,String name) throws Exception {
        onEdt(()->{
            var pane=(JComponent)named("use-evaluation-panel");
            var scn=(Container)named("istar-scenario-view");
            var combo=(JComboBox<?>)find(scn,c->c instanceof JComboBox);
            require(Objects.equals(combo.getSelectedItem(),key),"Expected execution context for "+name);
            var table=(JTable)find(scn,c->c instanceof JTable t&&t.isShowing()&&"Context".equals(t.getColumnName(0)));
            require(table!=null,"Expected Markings table");
            table.clearSelection();
            configure(table,206,144,180,100);
            panelImage(Path.of(base+"-original.png"),pane,665,475);
            var sorter=new javax.swing.table.TableRowSorter<>(table.getModel());
            var keep=Set.of("AuctionCompleted","ObserveBid","O_bid","StopAuction","BidNeverIncreases");
            sorter.setRowFilter(new RowFilter<javax.swing.table.TableModel,Integer>() {
                @Override public boolean include(Entry<? extends javax.swing.table.TableModel,? extends Integer> e){
                    return keep.contains(e.getStringValue(2));
                }
            });
            var oldSorter=table.getRowSorter();
            var oldColumns=visibleColumns(table,1,2,3);
            try {
                table.setRowSorter(sorter);
                configure(table,153,220,105);
                require(table.getRowCount()==5,"Expected five rows in the Markings excerpt");
                panelImage(Path.of(base+"-focused.png"),pane,550,210);
            } finally {
                table.setRowSorter(oldSorter);
                table.setColumnModel(oldColumns);
            }
            return null;
        });
    }

