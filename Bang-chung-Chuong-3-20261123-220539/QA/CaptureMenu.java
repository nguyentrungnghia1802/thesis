import java.awt.*;
import java.nio.file.*;
import javax.swing.*;
import javax.imageio.ImageIO;
import org.tzi.use.config.Options;
import org.tzi.use.gui.main.MainWindow;
import org.tzi.use.main.Session;
import org.tzi.use.runtime.MainPluginRuntime;
class CaptureMenu {
  static MainWindow window;
  static JMenu menu(Component[] items,String name){
    for(Component item:items) if(item instanceof JMenu m && m.getText().equals(name)) return m;
    throw new IllegalStateException(name);
  }
  public static void main(String[] args) throws Exception{
    Path root=Path.of(args[0]); Options.processArgs(new String[]{"-H="+root,"-nr","-it"});
    var runtime=MainPluginRuntime.run(root.resolve("lib/plugins"));
    SwingUtilities.invokeAndWait(()->{
      window=MainWindow.create(new Session(),runtime);
      window.setBounds(30,30,1280,800);
      window.setAlwaysOnTop(true);window.toFront();
    });
    Thread.sleep(1100);
    SwingUtilities.invokeAndWait(()->{
      JMenu plugins=menu(window.getJMenuBar().getComponents(),"Plugins");
      JMenu bridge=menu(plugins.getMenuComponents(),"JaCaMo");
      plugins.doClick();
      bridge.setPopupMenuVisible(true);
      if(!bridge.getPopupMenu().isShowing())bridge.getPopupMenu().show(bridge,bridge.getWidth(),0);
      if(!plugins.getPopupMenu().isShowing()||!bridge.getPopupMenu().isShowing())throw new IllegalStateException("Popups hidden");
    });
    Thread.sleep(850);
    var rect=window.getBounds();
    ImageIO.write(new Robot().createScreenCapture(rect),"png",Path.of(args[1]).toFile());
    System.exit(0);
  }
}
