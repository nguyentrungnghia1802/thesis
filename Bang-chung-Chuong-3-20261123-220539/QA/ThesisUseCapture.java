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
public final class ThesisUseCapture {
    private static MainWindow owner;
    private static ClassLoader pluginLoader;
    private static final AtomicReference<Throwable> asynchronousFailure=new AtomicReference<>();
    public static void main(String[] args)throws Exception {
        Thread.setDefaultUncaughtExceptionHandler((thread,error)->{error.printStackTrace();asynchronousFailure.compareAndSet(null,error);});
        Path installation=Path.of(args[0]).toAbsolutePath(),evidence=Path.of(args[1]).toAbsolutePath();Files.createDirectories(evidence);
        boolean counter=args.length>2&&args[2].equals("counter");
        Options.processArgs(new String[]{"-H="+installation,"-nr","-it"});
        var runtime=MainPluginRuntime.run(installation.resolve("lib/plugins"));
        var registeredPlugins=PluginRuntime.getInstance().getPlugins();
        for(String name:List.of("CSL Model","OAL State","iStar Model","iStarSCN State","JaCaMo"))
            require(registeredPlugins.values().stream().anyMatch(p->p.getPluginModel().getName().equals(name)),"Missing plugin "+name);
        var bridge=registeredPlugins.values().stream().filter(p->p.getPluginModel().getName().equals("JaCaMo")).findFirst().orElseThrow();
        var registeredPlugin=bridge.getPluginClass();
        require(registeredPlugin!=null,"Cannot load the registered JaCaMo plugin");
        pluginLoader=registeredPlugin.getClass().getClassLoader();
        var guard=pluginLoader.loadClass("org.tzi.use.plugins.jacamo.verify.api.EngineInstallationGuard");guard.getMethod("verify").invoke(null);
        System.out.println("PACKAGED_PLUGINS_OK engine="+guard.getProtectionDomain().getCodeSource().getLocation());
        var session=new Session();SwingUtilities.invokeAndWait(()->{owner=MainWindow.create(session,runtime);owner.setBounds(GraphicsEnvironment.getLocalGraphicsEnvironment().getMaximumWindowBounds());owner.setAlwaysOnTop(true);owner.toFront();});
        try {

            if(!counter){
                SwingUtilities.invokeAndWait(()->{
                    JMenu plugins=menu(owner.getJMenuBar().getComponents(),"Plugins");
                    JMenu jacamo=menu(plugins.getMenuComponents(),"JaCaMo");
                    MenuSelectionManager.defaultManager().setSelectedPath(
                        new MenuElement[]{owner.getJMenuBar(),plugins,plugins.getPopupMenu(),jacamo,jacamo.getPopupMenu()});
                });
                captureWindow(owner,evidence.resolve("S01-menu.png"));
                SwingUtilities.invokeAndWait(()->MenuSelectionManager.defaultManager().clearSelectedPath());
            }
            clickPluginMenu("JaCaMo","Run experiment...");

            waitFor(()->named("bridge-project")!=null,10,"run form");
            Path example=evidence.resolve("input");
            Path models=example;String base=counter?"counter":"auction";
            SwingUtilities.invokeAndWait(()->{
                ((JTextField)named("bridge-project")).setText(example.resolve(base+".jcm").toString());
                ((JTextField)named("bridge-csl")).setText(models.resolve(base+".csl").toString());
                ((JTextField)named("bridge-istar")).setText(models.resolve(base+".istar").toString());
                ((JTextField)named("bridge-mapping")).setText(models.resolve("attribute-mapping.xml").toString());

            });
            Window form=onEdt(()->Arrays.stream(Window.getWindows()).filter(w->w instanceof JDialog && w.isVisible()).findFirst().orElseThrow());
            if(!counter)captureWindow(form,evidence.resolve("S02-configuration.png"));
            SwingUtilities.invokeLater(()->button(form,"Run").doClick());
            waitFor(()->named("jacamo-evaluation-view")!=null,10,"embedded experiment view");

            var view=(JPanel)onEdt(()->named("jacamo-evaluation-view"));
            onEdt(()->{internalFrame("JaCaMo —").setMaximum(true);return null;});

            waitFor(()->runDirectory(view)!=null,20,"producer startup");Path work=onEdt(()->runDirectory(view));
            waitFor(()->completed(work,counter),35,"source verification");

            waitFor(()->{try{return Files.exists(work.resolve("checkpoint-"+object(object(readReport(work).get("response")).get("result")).get("sequence")+".json"));
            }catch(Exception error){return false;}},10,"final source receipt");
            var latest=readReport(work);var response=object(latest.get("response"));var request=object(latest.get("request"));
            var result=object(response.get("result"));
            require(counter?response.get("decision").equals("HOLD_FAILURE"):completedGoals(result)==2,"Live case did not meet terminal criterion");
            int seq=((Number)result.get("sequence")).intValue();
            Files.writeString(evidence.resolve("session.txt"),"run="+request.get("run")+"\nsequence="+seq+"\nsource-dir="+work+"\n");
            SwingUtilities.invokeAndWait(()->{
                selectTab(view,"Checkpoints");
                JTable timeline=(JTable)named("bridge-checkpoint-history");
                int selectedRow=-1;
                for(int row=0;row<timeline.getRowCount();row++)if(String.valueOf(seq).equals(String.valueOf(timeline.getValueAt(row,0)))){selectedRow=row;break;}
                require(selectedRow>=0,"Captured checkpoint missing from timeline");
                timeline.setRowSelectionInterval(selectedRow,selectedRow);
                timeline.scrollRectToVisible(timeline.getCellRect(selectedRow,0,true));
            });
            if(counter){
                captureWindow(owner,evidence.resolve("S06a-counter-checkpoint.png"));
                SwingUtilities.invokeAndWait(()->{selectTab(view,"Artifacts");selectTab(view,"OCL");resizeTable(view,"Artifact",58,141,153,100);resizeTable(view,"Object",90,139,90,105,43,50);});
                captureWindow(owner,evidence.resolve("S06b-counter-ocl.png"));
            }else{
                captureWindow(owner,evidence.resolve("S03-auction-checkpoint.png"));
                SwingUtilities.invokeAndWait(()->{selectTab(view,"Artifacts");resizeTable(view,"Artifact",50,148,293,105);selectTab(view,"OAL State");});
                captureWindow(owner,evidence.resolve("S04-auction-oal.png"));
                SwingUtilities.invokeAndWait(()->{
                    selectTab(view,"iStarSCN");
                    var scn=(Container)named("istar-scenario-view");
                    selectTab(scn,"Markings");
                });
                var combo=(JComboBox<?>)onEdt(()->find(named("istar-scenario-view"),c->c instanceof JComboBox<?>));
                require(onEdt(combo::getItemCount)==2,"Two iStar contexts are required for evidence");
                for(int index=0;index<2;index++){
                    final int i=index;
                    SwingUtilities.invokeAndWait(()->{
                        combo.setSelectedIndex(i);
                        var table=(JTable)find(named("istar-scenario-view"),c->c instanceof JTable);
                        for(int row=0;row<table.getRowCount();row++)if("AuctionCompleted".equals(table.getValueAt(row,2))){
                            table.setRowSelectionInterval(row,row);table.scrollRectToVisible(table.getCellRect(row,2,true));break;
                        }
                    });
                    captureWindow(owner,evidence.resolve("S05"+(index==0?"a":"b")+"-auction-marking.png"));
                }
            }
            exportState(evidence.resolve("checkpoint.oal"),models.resolve(base+".csl"),"OAL",result);
            exportState(evidence.resolve("checkpoint.iscn"),models.resolve(base+".istar"),"ISTAR_SCN",result);
            long pid=producerPid(view);
            SwingUtilities.invokeAndWait(()->{var frame=internalFrame("JaCaMo —");require(frame!=null,"Embedded USE frame disappeared");frame.doDefaultCloseAction();});
            waitFor(()->ProcessHandle.of(pid).isEmpty()||!ProcessHandle.of(pid).orElseThrow().isAlive(),8,"owned producer shutdown");
            require(!Files.exists(work.resolve("bridge-secret.hex")),"Run credential survived shutdown");

            Path saved=Files.createDirectories(evidence.resolve("run"));
            try(var files=Files.list(work)){
                for(Path file:files.filter(Files::isRegularFile).toList()){
                    String fileName=file.getFileName().toString();
                    if(fileName.matches("checkpoint-[0-9]+\\.json|consumer-history\\.jsonl|latest\\.json|producer\\.log"))
                        Files.copy(file,saved.resolve(fileName),StandardCopyOption.REPLACE_EXISTING);
                }
            }
            require(asynchronousFailure.get()==null,"Swing error: "+asynchronousFailure.get());
            Files.writeString(evidence.resolve("result.txt"),"PASS\ncase="+(counter?"counter_violation":"auction_valid")+"\nplugins=5\nowned_producer_stopped=true\ndecision="+response.get("decision")+"\ncompleted_auctions="+completedGoals(result)+"\n");
            System.out.println("EMBEDDED_USE_SMOKE_PASS case="+(counter?"counter":"auction")+" evidence="+evidence);
        }finally{
            SwingUtilities.invokeAndWait(()->{var frame=internalFrame("JaCaMo —");if(frame!=null)frame.doDefaultCloseAction();for(Window window:Window.getWindows())window.dispose();});
        }
        System.exit(0);
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
    private static long completedGoals(Map<String,Object> result){if(!(result.get("elements") instanceof List<?> list))return 0;return list.stream().map(ThesisUseCapture::object).filter(e->e.get("element").equals("AuctionCompleted")&&e.get("status").equals("FULFILLED")).count();}
    private static boolean completed(Path work,boolean counter){try{var response=object(readReport(work).get("response"));return counter?response.get("decision").equals("HOLD_FAILURE"):completedGoals(object(response.get("result")))==2;}catch(Exception ignored){return false;}}
    private static Path runDirectory(Container view){var label=(JLabel)find(view,c->c instanceof JLabel&&((JLabel)c).getToolTipText()!=null&&((JLabel)c).getToolTipText().startsWith("Run evidence: "));return label==null?null:Path.of(label.getToolTipText().substring(14));}
    private static long producerPid(JPanel view)throws Exception{var field=view.getClass().getDeclaredField("session");field.setAccessible(true);Object session=field.get(view);return (Long)session.getClass().getMethod("producerPid").invoke(session);}
    private static void exportState(Path file,Path model,String kind,Map<String,Object> result)throws Exception {
        Class<?> document=pluginLoader.loadClass("org.vnu.sme.goal.dsl.csl_marking.mm.ModelStateDocument"),kindType=pluginLoader.loadClass("org.vnu.sme.goal.dsl.csl_marking.mm.ModelStateDocument$Kind"),marking=pluginLoader.loadClass("org.vnu.sme.goal.dsl.csl_marking.mm.ModelStateDocument$Marking"),state=pluginLoader.loadClass("org.vnu.sme.goal.dsl.csl_marking.mm.AcceptedAolState");
        Object objects=document.getMethod("objects",List.class).invoke(null,result.get("state"));var markings=new ArrayList<Object>();
        for(Object raw:(List<?>)result.get("elements")){var e=object(raw);markings.add(marking.getConstructor(String.class,String.class,String.class,String.class).newInstance(e.get("context"),e.get("actor"),e.get("element"),e.get("status")));}
        Object instance=document.getConstructor(kindType,Path.class,String.class,state,List.class).newInstance(Enum.valueOf((Class)kindType,kind),model,result.get("sequence").toString(),objects,markings);document.getMethod("write",Path.class).invoke(instance,file);
    }

    private static void captureWindow(Window window,Path file)throws Exception {
        Thread.sleep(650);
        var bounds=onEdt(window::getBounds).intersection(window.getGraphicsConfiguration().getBounds());
        Toolkit.getDefaultToolkit().sync();
        ImageIO.write(new Robot(window.getGraphicsConfiguration().getDevice()).createScreenCapture(bounds),"png",file.toFile());
    }
    private static void resizeTable(Container view,String first,int... widths){
        var table=(JTable)find(view,c->c instanceof JTable t && t.isShowing() && first.equals(t.getColumnName(0)));
        if(table!=null)for(int i=0;i<widths.length;i++)table.getColumnModel().getColumn(i).setPreferredWidth(widths[i]);
    }
    private static void selectTab(Container root,String title){find(root,c->{if(c instanceof JTabbedPane tabs)for(int i=0;i<tabs.getTabCount();i++)if(tabs.getTitleAt(i).equals(title)){tabs.setSelectedIndex(i);return true;}return false;});}
    private static JInternalFrame internalFrame(String title){return owner==null?null:(JInternalFrame)find(owner,c->c instanceof JInternalFrame frame&&!frame.isClosed()&&frame.getTitle().startsWith(title));}
    private static JFileChooser chooser(){for(Window window:Window.getWindows())if(window.isVisible()){var found=find(window,c->c instanceof JFileChooser);if(found!=null)return (JFileChooser)found;}return null;}
    private static Component named(String name){for(Window window:Window.getWindows())if(window.isVisible()){var found=find(window,c->name.equals(c.getName()));if(found!=null)return found;}return null;}
    private static JButton button(Container root,String text){return (JButton)find(root,c->c instanceof JButton b&&b.getText().equals(text));}
    private static Component find(Component root,java.util.function.Predicate<Component> matches){if(matches.test(root))return root;if(root instanceof Container container)for(Component child:container.getComponents()){var result=find(child,matches);if(result!=null)return result;}return null;}
    private static <T>T onEdt(java.util.concurrent.Callable<T> action)throws Exception{var value=new AtomicReference<T>();var failure=new AtomicReference<Exception>();SwingUtilities.invokeAndWait(()->{try{value.set(action.call());}catch(Exception e){failure.set(e);}});if(failure.get()!=null)throw failure.get();return value.get();}
    private static void waitFor(BooleanSupplier condition,int seconds,String label)throws Exception {long until=System.nanoTime()+seconds*1_000_000_000L;while(System.nanoTime()<until){if(onEdt(condition::getAsBoolean))return;if(asynchronousFailure.get()!=null)throw new AssertionError("Asynchronous UI failure",asynchronousFailure.get());Thread.sleep(100);}throw new AssertionError("Timeout: "+label);}
    private static void require(boolean condition,String message){if(!condition)throw new AssertionError(message);}
}
