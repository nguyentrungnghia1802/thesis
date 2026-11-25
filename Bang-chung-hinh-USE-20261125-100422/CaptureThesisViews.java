import java.awt.*;
import java.awt.image.BufferedImage;
import java.nio.file.*;
import java.util.*;
import java.util.List;
import java.util.concurrent.atomic.AtomicReference;
import java.util.function.BooleanSupplier;
import javax.imageio.ImageIO;
import javax.swing.*;
import org.tzi.use.config.Options;
import org.tzi.use.gui.main.MainWindow;
import org.tzi.use.main.Session;
import org.tzi.use.runtime.*;
import org.tzi.use.runtime.impl.PluginRuntime;

/** Cold packaged USE check. Requires a display; all application classes come from the installation. */
public final class CaptureThesisViews {
    private static MainWindow owner;
    private static ClassLoader pluginLoader;
    private static final AtomicReference<Throwable> asynchronousFailure=new AtomicReference<>();
    public static void main(String[] args)throws Exception {
        Thread.setDefaultUncaughtExceptionHandler((thread,error)->{error.printStackTrace();asynchronousFailure.compareAndSet(null,error);});
        Path installation=Path.of(args[0]).toAbsolutePath(),evidence=Path.of(args[1]).toAbsolutePath();Files.createDirectories(evidence);
        String mode=args[3]; boolean counter=mode.startsWith("counter")||mode.equals("restored");
        Options.processArgs(new String[]{"-H="+installation,"-nr","-it"});
        var runtime=MainPluginRuntime.run(installation.resolve("lib/plugins"));
        var plugins=PluginRuntime.getInstance().getPlugins();
        for(String name:List.of("CSL Model","OAL State","iStar Model","iStarSCN State","JaCaMo"))
            require(plugins.values().stream().anyMatch(p->p.getPluginModel().getName().equals(name)),"Missing plugin "+name);
        var bridge=plugins.values().stream().filter(p->p.getPluginModel().getName().equals("JaCaMo")).findFirst().orElseThrow();
        var registeredPlugin=bridge.getPluginClass();
        require(registeredPlugin!=null,"Cannot load the registered JaCaMo plugin");
        pluginLoader=registeredPlugin.getClass().getClassLoader();
        var guard=pluginLoader.loadClass("org.tzi.use.plugins.jacamo.verify.api.EngineInstallationGuard");guard.getMethod("verify").invoke(null);
        System.out.println("PACKAGED_PLUGINS_OK engine="+guard.getProtectionDomain().getCodeSource().getLocation());
        var session=new Session();SwingUtilities.invokeAndWait(()->{owner=MainWindow.create(session,runtime);owner.setBounds(GraphicsEnvironment.getLocalGraphicsEnvironment().getMaximumWindowBounds());owner.setAlwaysOnTop(true);owner.toFront();});
        try {
            if (mode.equals("mapping")) {
                onEdt(() -> { var pluginMenu = menu(owner.getJMenuBar().getComponents(), "Plugins");
                    var submenu = menu(pluginMenu.getMenuComponents(), "JaCaMo");
                    var popup = submenu.getPopupMenu();
                    popup.setSize(popup.getPreferredSize());
                    popup.doLayout();
                    render(evidence.resolve("menu.png"), popup, popup.getWidth(), popup.getHeight());
                    return null; });
            }
            clickPluginMenu("JaCaMo","Run experiment...");
            waitFor(()->named("bridge-mrv")!=null,10,"MRV chooser");
            Path example=Path.of(args[2]).toAbsolutePath().getParent();
            Path models=example;String base=counter?"counter":"auction";
            SwingUtilities.invokeAndWait(()->{
                var select=(JFileChooser)named("bridge-mrv");
                require(!select.isAcceptAllFileFilterUsed()&&select.getFileFilter().accept(example.resolve(base+".mrv").toFile())
                        &&!select.getFileFilter().accept(example.resolve(base+".jcm").toFile()),"Expected an MRV-only filter");
                select.setSelectedFile(Path.of(args[2]).toFile());
                if (!mode.equals("mapping")) select.approveSelection();
            });
            if (mode.equals("mapping")) {
                Thread.sleep(800);
                onEdt(() -> {var select=(JFileChooser)named("bridge-mrv");
                    render(evidence.resolve("mrv.png"),select,select.getWidth(),select.getHeight());
                    select.approveSelection();
                    return null; });
            }
            waitFor(()->named("jacamo-evaluation-view")!=null,10,"embedded experiment view");
            var view=(JPanel)onEdt(()->named("jacamo-evaluation-view"));
            onEdt(()->{internalFrame("JaCaMo —").setMaximum(true);return null;});
            waitFor(()->runDirectory(view)!=null,20,"producer startup");Path work=onEdt(()->runDirectory(view));

            waitFor(()->ready(work,mode),40,"matching real verification result");
            List<Map<String,Object>> trace=records(work);
            var latest=trace.getLast();var response=object(latest.get("response"));var request=object(latest.get("request"));
            String run=request.get("run").toString();int last=seq(latest);
            var split=(JSplitPane)onEdt(()->find(view,c->c instanceof JSplitPane&&"jacamo-use-split".equals(c.getName())));
            waitFor(()->((JTable)named("bridge-checkpoint-history")).getRowCount()>=last,10,"Swing checkpoint history");
            int selected=last;
            String context="";
            if(mode.equals("mapping")) {
                var choice=trace.stream().filter(r->values(r,"best_bid").size()==2)
                        .filter(r->{var v=values(r,"best_bid");return v.values().stream().allMatch(n->n.doubleValue()<Double.MAX_VALUE)&&v.get("a1").doubleValue()!=v.get("a2").doubleValue();})
                        .findFirst().orElseGet(()->trace.stream().filter(r->values(r,"best_bid").size()==2).findFirst().orElseThrow());
                selected=seq(choice);
                show(view,split,selected,590,"Artifacts","Checkpoints");
                table(evidence.resolve("artifacts.png"),view,"Artifact",i->true,0,2);
                show(view,split,selected,230,"Artifacts","OAL State");
                diagram(evidence.resolve("oal.png"),view,"AolDiagram");
                compact(evidence.resolve("oal-compact.png"),view,"AolDiagram");
                show(view,split,1,230,"Artifacts","Checkpoints");
                table(evidence.resolve("timeline.png"),view,"Checkpoint",i->i<Math.min(8,last));
                show(view,split,last,230,"Artifacts","Checkpoints");
                table(evidence.resolve("terminal-timeline.png"),view,"Checkpoint",i->i>=last-5&&i<last);
                table(evidence.resolve("terminal-artifacts.png"),view,"Artifact",i->true,0,2);
                show(view,split,last,230,"Artifacts","OAL State");
                diagram(evidence.resolve("terminal-oal.png"),view,"AolDiagram");
                show(view,split,last,230,"Artifacts","iStarSCN");
                for (String id:List.of("a1","a2")) {
                    var result=object(response.get("result"));
                    var state=rows(result.get("state")).stream().filter(row->("'"+id+"'").equals(row.get("id"))).findFirst().orElseThrow();
                    var key=state.get("object").toString();
                    require(rows(result.get("elements")).stream().anyMatch(row->"AuctionCompleted".equals(row.get("element"))&&"FULFILLED".equals(row.get("status"))&&key.equals(row.get("context"))),"Missing terminal Goal for "+id);
                    context(view,key,"Diagram");
                    show(view,split,last,230,"Artifacts","iStarSCN");
                    context(view,key,"Diagram");
                    diagram(evidence.resolve("istar-"+id+".png"),view,"IStarDiagram");
                    compact(evidence.resolve("istar-"+id+"-compact.png"),view,"IStarDiagram");
                    context(view,key,"Markings");
                    table(evidence.resolve("markings-"+id+".png"),view,"Context",i->true,1,2,3);
                }
                show(view,split,last,230,"Artifacts","CSL Model");
                diagram(evidence.resolve("csl.png"),view,"CslDiagram");
                show(view,split,last,230,"Artifacts","iStar Model");
                diagram(evidence.resolve("istar-model.png"),view,"IStarDiagram");
            } else if(mode.equals("goal")) {
                require(response.get("decision").equals("HOLD_FAILURE"),"Wrong hold decision");
                var previous=trace.get(trace.size()-2);
                var before=values(previous,"best_bid");var after=values(latest,"best_bid");
                String auction=after.keySet().stream().filter(k->n(before.get(k),10)&&n(after.get(k),20)).findFirst().orElseThrow();
                var result=object(response.get("result"));
                var marking=rows(result.get("elements")).stream().filter(r->r.get("element").equals("BidNeverIncreases")&&r.get("status").equals("VIOLATED"))
                       .filter(r->rows(result.get("state")).stream().anyMatch(s->s.get("object").equals(r.get("context"))&&s.get("id").equals("'"+auction+"'"))).findFirst().orElseThrow();
                context=marking.get("context").toString();
                var inv=rows(result.get("checks")).stream().filter(c->c.get("kind").equals("CSL_INVARIANT")).toList();
                require(!inv.isEmpty()&&inv.stream().allMatch(c->c.get("verdict").equals("PASS")),"Not all invariants PASS");
                require(seq(previous)==last-1,"Snapshots not adjacent");
                show(view,split,last-1,560,"Artifacts","Checkpoints");
                table(evidence.resolve("before.png"),view,"Artifact",i->true,0,2);
                show(view,split,last,560,"Artifacts","Checkpoints");
                table(evidence.resolve("after.png"),view,"Artifact",i->true,0,2);
                table(evidence.resolve("hold.png"),view,"Checkpoint",i->i>=last-3&&i<last);
                show(view,split,last,490,"Artifacts","iStarSCN");
                context(view,context,"Markings");
                table(evidence.resolve("markings.png"),view,"Context",i->true,1,2,3);
                show(view,split,last,240,"Console","OCL");
                table(evidence.resolve("ocl.png"),view,"Object",i->true,0,1,2,4);
                filterTable(evidence.resolve("invariants.png"),view,"Object",r->"CSL_INVARIANT".equals(r.getValue(2)),0,1,4);
            } else if(mode.equals("missing")) {
                require(response.get("decision").equals("HOLD_UNVERIFIED")
                        && response.get("diagnostic").toString().contains("ATTRIBUTE_VALUE_MISSING:Auction.best_bid"),"Wrong missing data decision");
                show(view,split,last,660,"Console","Checkpoints");
                table(evidence.resolve("hold.png"),view,"Checkpoint",i->i>=last-3&&i<last);
                waitFor(()->find(view,c->c instanceof JLabel l&&l.getText().contains("ATTRIBUTE_VALUE_MISSING:Auction.best_bid"))!=null,6,"projection diagnostic");
                onEdt(()->{
                    var diagnostic=(JLabel)find(view,c->c instanceof JLabel l&&l.getText().contains("ATTRIBUTE_VALUE_MISSING:Auction.best_bid"));
                    Dimension size=diagnostic.getPreferredSize();
                    Dimension before=diagnostic.getSize();
                    diagnostic.setSize(size.width+48,size.height+4);
                    try { render(evidence.resolve("diagnostic.png"),diagnostic,size.width+48,size.height+4); }
                    finally { diagnostic.setSize(before); }
                    return null;
                });
            } else {
                int expected=mode.equals("restored")?2:-1;
                require(n(values(latest,"value").get("counter"),expected),"Wrong final Counter value");
                if (!mode.equals("counterbase")) require(Files.readString(work.resolve("producer.log")).contains("COUNTER_WITNESS value=-1"),"No negative witness");
                show(view,split,last,730,"Console","OCL");
                if (!mode.equals("counterbase")) console(evidence.resolve("console.png"),view,List.of("COUNTER_WITNESS"));
                table(evidence.resolve("ocl.png"),view,"Object",i->true,1,2,3,4);
                show(view,split,last,730,"Artifacts","Checkpoints");
                table(evidence.resolve("hold.png"),view,"Checkpoint",i->i<last);
            }
            Files.writeString(evidence.resolve("selection.txt"),"run="+run+"\nlatest="+last+"\nselected="+selected+
                    "\ncontext="+context+"\nvalues="+values(trace.get(selected-1),mode.startsWith("counter")||mode.equals("restored")?"value":"best_bid")+"\ndecision="+response.get("decision")+"\n");
            Files.copy(work.resolve("consumer-history.jsonl"),evidence.resolve("consumer-history.jsonl"),StandardCopyOption.REPLACE_EXISTING);
            Files.copy(work.resolve("producer.log"),evidence.resolve("producer.log"),StandardCopyOption.REPLACE_EXISTING);
            for(int sequence:new TreeSet<>(List.of(last,Math.max(1,last-1),selected))) {
                Path file=work.resolve("checkpoint-"+sequence+".json");
                waitFor(()->Files.isRegularFile(file),6,"source receipt "+sequence);
                Files.copy(file,evidence.resolve(file.getFileName()),StandardCopyOption.REPLACE_EXISTING);
            }
            long pid=producerPid(view);
            SwingUtilities.invokeAndWait(()->{var frame=internalFrame("JaCaMo —");require(frame!=null,"Embedded USE frame disappeared");frame.doDefaultCloseAction();});
            waitFor(()->ProcessHandle.of(pid).isEmpty()||!ProcessHandle.of(pid).orElseThrow().isAlive(),8,"owned producer shutdown");
            require(!Files.exists(work.resolve("bridge-secret.hex")),"Run credential survived shutdown");
            require(asynchronousFailure.get()==null,"Swing error: "+asynchronousFailure.get());
            
            System.out.println("EMBEDDED_USE_SMOKE_PASS case="+(counter?"counter":"auction")+" evidence="+evidence);
        }finally{
            SwingUtilities.invokeAndWait(()->{var frame=internalFrame("JaCaMo —");if(frame!=null)frame.doDefaultCloseAction();for(Window window:Window.getWindows())window.dispose();});
        }
        System.exit(0);
    }

    private static boolean n(Number n,double value){return n!=null&&n.doubleValue()==value;}
    private static int seq(Map<String,Object> row){return ((Number)object(object(row.get("request")).get("snapshot")).get("sequence")).intValue();}
    private static List<Map<String,Object>> rows(Object value){return ((List<?>)value).stream().map(CaptureThesisViews::object).toList();}
    private static List<Map<String,Object>> records(Path folder)throws Exception {
        var decoder=pluginLoader.loadClass("org.tzi.use.plugins.jacamo.bridge.protocol.CanonicalJson").getMethod("decode",byte[].class);
        var values=new ArrayList<Map<String,Object>>();
        for(String line:Files.readAllLines(folder.resolve("consumer-history.jsonl"))) {
            if(!line.isBlank())values.add(object(decoder.invoke(null,(Object)line.getBytes(java.nio.charset.StandardCharsets.UTF_8))));
        }
        return values;
    }
    private static Map<String,Number> values(Map<String,Object> row,String attr) {
        var snapshot=object(object(row.get("request")).get("snapshot"));
        var result=new TreeMap<String,Number>();
        for(var a:rows(snapshot.get("artifacts"))) {
            String name=a.get("name").toString();
            if(Set.of("a1","a2","counter").contains(name)&&object(a.get("properties")).get(attr) instanceof Number n)
                result.put(name,n);
        }
        return result;
    }
    private static boolean ready(Path work,String mode) {
        try {
            var latest=readReport(work); int s=seq(latest);
            var response=object(latest.get("response")); String decision=response.get("decision").toString();
            if(!Files.isRegularFile(work.resolve("checkpoint-"+s+".json")))return false;
            return switch(mode){
                case "mapping" -> completedGoals(object(response.get("result")))==2;
                case "goal","counter","counterbase" -> decision.equals("HOLD_FAILURE");
                case "missing" -> decision.equals("HOLD_UNVERIFIED");
                case "restored" -> n(values(latest,"value").get("counter"),2)&&decision.equals("APPROVE");
                default -> throw new IllegalArgumentException(mode);
            };
        }catch(Exception transientInput){return false;}
    }
    private static void configure(JTable t,int... widths){
        t.setAutoResizeMode(JTable.AUTO_RESIZE_OFF);
        for(int i=0;i<widths.length;i++){
            var c=t.getColumnModel().getColumn(i);
            c.setPreferredWidth(widths[i]);c.setWidth(widths[i]);
        }
    }
    private static void show(Container view,JSplitPane split,int sequence,int divider,String left,String right)throws Exception {
        SwingUtilities.invokeAndWait(()->{
            split.setDividerLocation(divider);selectTab(view,left);selectTab(view,"Checkpoints");
            var timeline=(JTable)named("bridge-checkpoint-history");
            int row=sequence-1;
            require(row<timeline.getRowCount(),"No displayed checkpoint");
            Object rowSeq=timeline.getValueAt(row,0);
            require(rowSeq.toString().equals(Integer.toString(sequence))||rowSeq.equals("?"),"UI/trace sequence mismatch");
            timeline.setRowSelectionInterval(row,row);
            timeline.scrollRectToVisible(timeline.getCellRect(Math.min(row+4,timeline.getRowCount()-1),0,true));
            configure(timeline,80,58,271,135,103,117,122);
            selectTab(view,right);
            var artifacts=(JTable)find(view,c->c instanceof JTable t && t.isShowing() && "Artifact".equals(t.getColumnName(0)));
            if(artifacts!=null)configure(artifacts,50,173,500,115);
            var ocl=(JTable)find(view,c->c instanceof JTable t && t.isShowing() && "Condition".equals(t.getColumnName(1)));
            if(ocl!=null)configure(ocl,229,274,123,260,56,89);
        });
        Thread.sleep(550);
    }
    private record Tool(String menu,Path file,String title){}

    private static void clickPluginMenu(String group, String label) throws Exception {
        SwingUtilities.invokeAndWait(() -> {
            JMenu plugins = menu(owner.getJMenuBar().getComponents(), "Plugins");
            JMenu submenu = menu(plugins.getMenuComponents(), group);
            for (Component component : submenu.getMenuComponents()) {
                if (component instanceof JMenuItem item && label.equals(item.getText())) {
                    require(item.isEnabled(), "Disabled plugin menu item: " + group + " / " + label);
                    item.doClick();
                    return;
                }
            }
            throw new AssertionError("Missing plugin menu item: " + group + " / " + label);
        });
    }

    private static JMenu menu(Component[] components, String label) {
        for (Component component : components) {
            if (component instanceof JMenu item && label.equals(item.getText())) return item;
        }
        throw new AssertionError("Missing menu: " + label);
    }
    private static Map<String,Object> object(Object value){return (Map<String,Object>)value;}
    private static Map<String,Object> readReport(Path work)throws Exception{return object(pluginLoader.loadClass("org.tzi.use.plugins.jacamo.bridge.protocol.CanonicalJson").getMethod("decode",byte[].class).invoke(null,(Object)Files.readAllBytes(work.resolve("latest.json"))));}
    private static long completedGoals(Map<String,Object> result){if(!(result.get("elements") instanceof List<?> list))return 0;return list.stream().map(CaptureThesisViews::object).filter(e->e.get("element").equals("AuctionCompleted")&&e.get("status").equals("FULFILLED")).count();}
    private static boolean completed(Path work,boolean counter){try{var response=object(readReport(work).get("response"));return counter?response.get("decision").equals("HOLD_FAILURE"):completedGoals(object(response.get("result")))==2;}catch(Exception ignored){return false;}}
    private static Path runDirectory(Container view){var label=(JLabel)find(view,c->c instanceof JLabel&&((JLabel)c).getToolTipText()!=null&&((JLabel)c).getToolTipText().startsWith("Run evidence: "));return label==null?null:Path.of(label.getToolTipText().substring(14));}
    private static long producerPid(JPanel view)throws Exception{var field=view.getClass().getDeclaredField("session");field.setAccessible(true);Object session=field.get(view);return (Long)session.getClass().getMethod("producerPid").invoke(session);}
    private static void exportState(Path file,Path model,String kind,Map<String,Object> result)throws Exception {
        Class<?> document=pluginLoader.loadClass("org.vnu.sme.goal.dsl.csl_marking.mm.ModelStateDocument"),kindType=pluginLoader.loadClass("org.vnu.sme.goal.dsl.csl_marking.mm.ModelStateDocument$Kind"),marking=pluginLoader.loadClass("org.vnu.sme.goal.dsl.csl_marking.mm.ModelStateDocument$Marking"),state=pluginLoader.loadClass("org.vnu.sme.goal.dsl.csl_marking.mm.AcceptedAolState");
        Object objects=document.getMethod("objects",List.class).invoke(null,result.get("state"));var markings=new ArrayList<Object>();
        for(Object raw:(List<?>)result.get("elements")){var e=object(raw);markings.add(marking.getConstructor(String.class,String.class,String.class,String.class).newInstance(e.get("context"),e.get("actor"),e.get("element"),e.get("status")));}
        Object instance=document.getConstructor(kindType,Path.class,String.class,state,List.class).newInstance(Enum.valueOf((Class)kindType,kind),model,result.get("sequence").toString(),objects,markings);document.getMethod("write",Path.class).invoke(instance,file);
    }

    private static void selectTree(JTree tree,String... labels){
        if(tree==null)return;
        for(int i=0;i<tree.getRowCount();i++)tree.expandRow(i);
        for(int i=0;i<tree.getRowCount();i++){
            String label=tree.getPathForRow(i).getLastPathComponent().toString();
            for(String expected:labels)if(label.equals(expected)||label.endsWith(" "+expected)){
                tree.setSelectionRow(i);return;
            }
        }
    }
    private static void render(Path file, Component component, int width, int height) throws Exception {
        require(width > 0 && height > 0 && width < 7000 && height < 7000, "Invalid print bounds "+width+"x"+height+" for "+file);
        var image = new BufferedImage(width*2,height*2,BufferedImage.TYPE_INT_RGB);
        var g = image.createGraphics();
        g.scale(2,2);
        g.setColor(Color.WHITE);
        g.fillRect(0,0,width,height);
        g.setRenderingHint(RenderingHints.KEY_TEXT_ANTIALIASING, RenderingHints.VALUE_TEXT_ANTIALIAS_ON);
        g.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
        component.printAll(g);
        g.dispose();
        ImageIO.write(image,"png",file.toFile());
        System.out.println("View "+file.getFileName()+" "+width+"x"+height);
    }
    private static void diagram(Path file,Container view,String type) throws Exception {
        onEdt(()->{
            Component diagram=find(view,c->c.isShowing()&&type.equals(c.getClass().getSimpleName()));
            require(diagram!=null,"Missing visible "+type);
            Dimension current=diagram.getSize();
            try {
                for(int pass=0;pass<2;pass++) {
                    Dimension full=diagram.getPreferredSize();
                    diagram.setSize(full);
                    render(file,diagram,full.width,full.height);
                }
            } finally { diagram.setSize(current); }
            return null;
        });
    }
    private static void compact(Path file,Container view,String type) throws Exception {
        onEdt(()->{
            var diagram=(org.tzi.use.gui.views.diagrams.DiagramView)find(view,c->c.isShowing()&&type.equals(c.getClass().getSimpleName()));
            var nodes=new LinkedHashMap<String,org.tzi.use.gui.views.diagrams.elements.PlaceableNode>();
            diagram.getGraph().iterator().forEachRemaining(n->nodes.put(n.getId(),n));
            if(type.equals("AolDiagram")) {
                var ordered=nodes.values().stream().sorted(Comparator.comparingDouble(org.tzi.use.gui.views.diagrams.elements.PlaceableNode::getX)).toList();
                var agents=ordered.stream().filter(n->n.getY()<80).toList();
                var roles=ordered.stream().filter(n->n.name().contains(" : participant")||n.name().contains(" : auctioneer")).toList();
                if(roles.size()!=5) {
                    roles=ordered.stream().filter(n->n.getY()>250&&n.getY()<370).toList();
                }
                require(agents.size()==5&&roles.size()==5,"Unexpected OAL canvas lanes: "+agents.size()+", "+roles.size());
                for(int i=0;i<5;i++) {
                    double x=i<3?28+i*356:190+(i-3)*356;
                    agents.get(i).setPosition(x,i<3?22:578);
                    roles.get(i).setPosition(x,i<3?125:484);
                }
                for(var n:ordered) {
                    if(agents.contains(n)||roles.contains(n))continue;
                    var info=n.getClass().getMethod("node").invoke(n);
                    String label=info.getClass().getField("label").get(info).toString();
                    if(label.startsWith("a1 "))n.setPosition(544,239);
                    else if(label.startsWith("a2 "))n.setPosition(163,239);
                    else if(label.startsWith("agrp "))n.setPosition(83,409);
                    else if(label.startsWith("aorg "))n.setPosition(685,409);
                }
            } else {
                locate(nodes,"Auctioneer",42,523);
                locate(nodes,"AuctionGroup",142,107);
                locate(nodes,"Participant",754,523);
                locate(nodes,"auction_capabilities",35,811);
                locate(nodes,"D_start",52,419);
                locate(nodes,"D_decide",285,417);
                locate(nodes,"D_bid",759,418);
                System.out.println("iStar native nodes="+nodes.keySet());
            }
            for(var node:nodes.values())diagram.invalidateNode(node);
            Dimension old=diagram.getSize();
            try {
                diagram.setSize(1550,1150);
                var probe=new BufferedImage(1550,1150,BufferedImage.TYPE_INT_RGB);
                var graphics=probe.createGraphics();
                diagram.printAll(graphics);
                graphics.dispose();
                Dimension size=diagram.getPreferredSize();
                diagram.setSize(size.width+55,size.height+28);
                render(file,diagram,diagram.getWidth(),diagram.getHeight());
            } finally { diagram.setSize(old); }
            return null;
        });
    }
    private static void locate(Map<String,org.tzi.use.gui.views.diagrams.elements.PlaceableNode> nodes,String key,double x,double y) {
        var node=nodes.get(key);
        if(node==null)node=nodes.values().stream().filter(n->n.name().equals(key)||n.getId().endsWith(":"+key)).findFirst().orElse(null);
        if(node!=null)node.setPosition(x,y);
    }
    private static void context(Container view,String key,String tab) throws Exception {
        onEdt(()->{var scn=(Container)named("istar-scenario-view");selectTab(scn,tab);
            var combo=(JComboBox<?>)find(scn,c->c instanceof JComboBox<?>);
            combo.setSelectedItem(key);
            require(key.equals(combo.getSelectedItem()),"Wrong iStar context");
            return null;});
        Thread.sleep(180);
    }
    private static void table(Path file,Container view,String heading,java.util.function.IntPredicate rows,int... columns) throws Exception {
        filterTable(file,view,heading,r->rows.test(r.getIdentifier()),columns);
    }
    private static void filterTable(Path file,Container view,String heading,java.util.function.Predicate<RowFilter.Entry<? extends javax.swing.table.TableModel,? extends Integer>> filter,int... columns) throws Exception {
        onEdt(()->{
            var table=(JTable)find(view,c->c instanceof JTable t&&t.isShowing()&&t.getColumnName(0).equals(heading));
            require(table!=null,"Missing visible table "+heading);
            var full=table.getColumnModel();
            var subset=new javax.swing.table.DefaultTableColumnModel();
            var font=table.getFontMetrics(table.getFont());
            var sorter=new javax.swing.table.TableRowSorter<>(table.getModel());
            sorter.setRowFilter(new RowFilter<javax.swing.table.TableModel,Integer>() {
                public boolean include(Entry<? extends javax.swing.table.TableModel,? extends Integer> entry){return filter.test(entry);}
            });
            int oldRow=table.getSelectedRow();
            var selection=(DefaultListSelectionModel)table.getSelectionModel();
            var listeners=selection.getListSelectionListeners();
            if(heading.equals("Checkpoint")) for(var l:listeners) selection.removeListSelectionListener(l);
            var oldSorter=table.getRowSorter();
            Dimension previous=table.getSize();
            int oldHeight=table.getRowHeight();
            var printPanel=new JComponent() {
                @Override protected void paintComponent(Graphics g){
                    table.getTableHeader().printAll(g);
                    Graphics body=g.create(0,table.getTableHeader().getHeight(),table.getWidth(),table.getHeight());
                    table.printAll(body);
                    body.dispose();
                }
            };
            try {
                table.setRowSorter(sorter);
                if(columns.length==0) for(int i=0;i<full.getColumnCount();i++) subset.addColumn(full.getColumn(i));
                else for(int i:columns) subset.addColumn(full.getColumn(i));
                table.setColumnModel(subset);
                table.setRowHeight(18);
                int width=0;
                for(int i=0;i<table.getColumnCount();i++){
                    var column=subset.getColumn(i);
                    int fitted=font.stringWidth(table.getColumnName(i))+22;
                    for(int j=0;j<table.getRowCount();j++) fitted=Math.max(fitted, font.stringWidth(Objects.toString(table.getValueAt(j,i),""))+18);
                    if (heading.equals("Checkpoint") && i==2) fitted=Math.min(288,fitted);
                    column.setMinWidth(20);
                    column.setWidth(fitted);
                    column.setPreferredWidth(fitted);
                    width+=fitted;
                }
                require(table.getRowCount()>0,"No table rows for "+file);
                table.setSize(width,table.getRowCount()*table.getRowHeight());
                int row=oldRow>=0?table.convertRowIndexToView(oldRow):-1;
                if(row>=0) selection.setSelectionInterval(row,row);
                var header=table.getTableHeader();
                header.setSize(width,header.getPreferredSize().height);
                printPanel.setSize(width,header.getHeight()+table.getHeight());
                render(file,printPanel,printPanel.getWidth(),printPanel.getHeight());
            } finally {
                table.setColumnModel(full);
                table.setRowSorter(oldSorter);
                table.setRowHeight(oldHeight);
                table.setSize(previous);
                if(oldRow>=0&&oldRow<table.getRowCount()) selection.setSelectionInterval(oldRow,oldRow);
                if(heading.equals("Checkpoint")) for(int i=listeners.length-1;i>=0;i--) selection.addListSelectionListener(listeners[i]);
            }
            return null;
        });
    }
    private static void console(Path file,Container view,List<String> needles) throws Exception {
        waitFor(()->{
            var pane=(JTextArea)find(view,c->c instanceof JTextArea a&&a.isShowing());
            return pane!=null&&needles.stream().allMatch(n->pane.getText().contains(n));
        },8,"Console messages "+needles);
        onEdt(()->{
            var pane=(JTextArea)find(view,c->c instanceof JTextArea a&&a.isShowing());
            var lines=pane.getText().lines().filter(l->needles.stream().anyMatch(l::contains)).toList();
            var excerpt=new JTextArea(String.join("\n",lines));
            excerpt.setFont(pane.getFont());
            excerpt.setBackground(pane.getBackground());
            excerpt.setForeground(pane.getForeground());
            excerpt.setLineWrap(true);
            excerpt.setWrapStyleWord(true);
            excerpt.setBorder(BorderFactory.createEmptyBorder(6,8,6,8));
            int longest=lines.stream().mapToInt(l->pane.getFontMetrics(pane.getFont()).stringWidth(l)).max().orElseThrow();
            excerpt.setSize(Math.min(longest+26,740),500);
            excerpt.setSize(excerpt.getWidth(),excerpt.getPreferredSize().height);
            render(file,excerpt,excerpt.getWidth(),excerpt.getHeight());
            return null;});
    }
    private static void selectTab(Container root,String title){find(root,c->{if(c instanceof JTabbedPane tabs)for(int i=0;i<tabs.getTabCount();i++)if(tabs.getTitleAt(i).equals(title)){tabs.setSelectedIndex(i);return true;}return false;});}
    private static JInternalFrame internalFrame(String title){return owner==null?null:(JInternalFrame)find(owner,c->c instanceof JInternalFrame frame&&!frame.isClosed()&&frame.getTitle().startsWith(title));}
    private static JFileChooser chooser(){for(Window window:Window.getWindows())if(window.isVisible()){var found=find(window,c->c instanceof JFileChooser);if(found!=null)return (JFileChooser)found;}return null;}
    private static Component named(String name){for(Window window:Window.getWindows())if(window.isVisible()){var found=find(window,c->name.equals(c.getName()));if(found!=null)return found;}return null;}
    private static Component find(Component root,java.util.function.Predicate<Component> matches){if(matches.test(root))return root;if(root instanceof Container container)for(Component child:container.getComponents()){var result=find(child,matches);if(result!=null)return result;}return null;}
    private static <T>T onEdt(java.util.concurrent.Callable<T> action)throws Exception{var value=new AtomicReference<T>();var failure=new AtomicReference<Exception>();SwingUtilities.invokeAndWait(()->{try{value.set(action.call());}catch(Exception e){failure.set(e);}});if(failure.get()!=null)throw failure.get();return value.get();}
    private static void waitFor(BooleanSupplier condition,int seconds,String label)throws Exception {long until=System.nanoTime()+seconds*1_000_000_000L;while(System.nanoTime()<until){if(onEdt(condition::getAsBoolean))return;if(asynchronousFailure.get()!=null)throw new AssertionError("Asynchronous UI failure",asynchronousFailure.get());Thread.sleep(100);}throw new AssertionError("Timeout: "+label);}
    private static void require(boolean condition,String message){if(!condition)throw new AssertionError(message);}
}

