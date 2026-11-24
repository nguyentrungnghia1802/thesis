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
public final class CaptureThesisCases {
    private static MainWindow owner;
    private static ClassLoader pluginLoader;
    private static final AtomicReference<Throwable> asynchronousFailure=new AtomicReference<>();
    public static void main(String[] args)throws Exception {
        Thread.setDefaultUncaughtExceptionHandler((thread,error)->{error.printStackTrace();asynchronousFailure.compareAndSet(null,error);});
        Path installation=Path.of(args[0]).toAbsolutePath(),evidence=Path.of(args[1]).toAbsolutePath();Files.createDirectories(evidence);
        String mode=args[3]; boolean counter=mode.equals("counter")||mode.equals("restored");
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
            clickPluginMenu("JaCaMo","Run experiment...");
            waitFor(()->named("bridge-mrv")!=null,10,"MRV chooser");
            Path example=Path.of(args[2]).toAbsolutePath().getParent();
            Path models=example;String base=counter?"counter":"auction";
            SwingUtilities.invokeAndWait(()->{
                var select=(JFileChooser)named("bridge-mrv");
                require(!select.isAcceptAllFileFilterUsed()&&select.getFileFilter().accept(example.resolve(base+".mrv").toFile())
                        &&!select.getFileFilter().accept(example.resolve(base+".jcm").toFile()),"Expected an MRV-only filter");
                select.setSelectedFile(Path.of(args[2]).toFile());
                select.approveSelection();
            });
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
                capture(evidence.resolve("source-original.png"));
                show(view,split,selected,230,"Artifacts","OAL State");
                capture(evidence.resolve("oal-original.png"));
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
                show(view,split,last-1,560,"Artifacts","Checkpoints");capture(evidence.resolve("before-original.png"));
                show(view,split,last,560,"Artifacts","Checkpoints");capture(evidence.resolve("hold-original.png"));
                show(view,split,last,490,"Artifacts","iStarSCN");
                final String selectedContext=context;
                SwingUtilities.invokeAndWait(()->{
                    var scn=(Container)named("istar-scenario-view");
                    selectTab(scn,"Markings");
                    var combo=(JComboBox<?>)find(scn,c->c instanceof JComboBox<?>);
                    combo.setSelectedItem(selectedContext);
                    require(selectedContext.equals(combo.getSelectedItem()),"Cannot select violating context");
                    var markings=(JTable)find(scn,c->c instanceof JTable t && t.isShowing());
                    configure(markings,238,132,169,97);
                    for(int i=0;i<markings.getRowCount();i++)if("BidNeverIncreases".equals(markings.getValueAt(i,2))){
                        require("VIOLATED".equals(markings.getValueAt(i,3)),"Marking did not match frozen cut");
                        markings.setRowSelectionInterval(i,i);
                        markings.scrollRectToVisible(markings.getCellRect(i,0,true));
                        return;
                    }
                    throw new AssertionError("Missing Goal row");
                });
                capture(evidence.resolve("marking-original.png"));
                show(view,split,last,240,"Console","OCL");
                capture(evidence.resolve("ocl-original.png"));
            } else if(mode.equals("missing")) {
                require(response.get("decision").equals("HOLD_UNVERIFIED")
                        && response.get("diagnostic").toString().contains("ATTRIBUTE_VALUE_MISSING:Auction.best_bid"),"Wrong missing data decision");
                show(view,split,last,660,"Console","Checkpoints");capture(evidence.resolve("hold-original.png"));
            } else {
                int expected=mode.equals("restored")?2:-1;
                require(n(values(latest,"value").get("counter"),expected),"Wrong final Counter value");
                require(Files.readString(work.resolve("producer.log")).contains("COUNTER_WITNESS value=-1"),"No negative witness");
                show(view,split,last,730,"Console","OCL");capture(evidence.resolve("counter-original.png"));
                show(view,split,last,730,"Console","Checkpoints");capture(evidence.resolve("checkpoints-original.png"));
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
    private static List<Map<String,Object>> rows(Object value){return ((List<?>)value).stream().map(CaptureThesisCases::object).toList();}
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
                case "goal","counter" -> decision.equals("HOLD_FAILURE");
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
    private static long completedGoals(Map<String,Object> result){if(!(result.get("elements") instanceof List<?> list))return 0;return list.stream().map(CaptureThesisCases::object).filter(e->e.get("element").equals("AuctionCompleted")&&e.get("status").equals("FULFILLED")).count();}
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
    private static void capture(Path file)throws Exception{
        Thread.sleep(600);
        var image=onEdt(()->{
            var capture=new BufferedImage(owner.getWidth(),owner.getHeight(),BufferedImage.TYPE_INT_RGB);
            var graphics=capture.createGraphics();
            owner.printAll(graphics);
            graphics.dispose();
            return capture;
        });
        ImageIO.write(image,"png",file.toFile());
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
