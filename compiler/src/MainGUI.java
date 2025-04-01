import javax.swing.*;
import javax.swing.border.EmptyBorder;
import java.awt.*;
import java.awt.event.*;
import java.io.*;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.List;
import java.util.ArrayList;
import java.util.Map;
import java.util.HashMap;
import javax.imageio.ImageIO;
import java.awt.image.BufferedImage;

public class MainGUI extends JFrame {

    private JTextField fileField;
    private JTextField lexerNameField;
    private JTextArea logArea;
    private ZoomableImagePanel zoomPanel;
    private JSlider zoomSlider;
    private JButton browseButton;
    private JButton generateButton;
    private JButton refreshImageButton;
    private JTabbedPane tabbedPane;

    public MainGUI() {
        setTitle("Generador de Lexer - Interfaz Moderna");
        setSize(800, 600);
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setLocationRelativeTo(null);
        initLookAndFeel();
        initComponents();
    }

    // Configuramos Nimbus para una apariencia moderna
    private void initLookAndFeel() {
        try {
            for (UIManager.LookAndFeelInfo info : UIManager.getInstalledLookAndFeels()) {
                if ("Nimbus".equals(info.getName())) {
                    UIManager.setLookAndFeel(info.getClassName());
                    break;
                }
            }
        } catch (Exception e) {
            // Si falla, se usará el look and feel por defecto
            e.printStackTrace();
        }
    }

    private void initComponents() {
        // Panel superior de entrada con colores modernos
        JPanel inputPanel = new JPanel(new GridBagLayout());
        inputPanel.setBackground(new Color(240, 248, 255)); // Azul muy claro
        inputPanel.setBorder(new EmptyBorder(10, 10, 10, 10));
        GridBagConstraints gbc = new GridBagConstraints();
        gbc.insets = new Insets(8, 8, 8, 8);
        gbc.fill = GridBagConstraints.HORIZONTAL;

        // Archivo YAL
        gbc.gridx = 0;
        gbc.gridy = 0;
        JLabel fileLabel = new JLabel("Archivo YAL:");
        fileLabel.setForeground(new Color(0, 70, 140));
        inputPanel.add(fileLabel, gbc);

        fileField = new JTextField();
        gbc.gridx = 1;
        gbc.weightx = 1.0;
        inputPanel.add(fileField, gbc);

        browseButton = new JButton("Examinar");
        gbc.gridx = 2;
        gbc.weightx = 0;
        inputPanel.add(browseButton, gbc);

        // Nombre del Lexer
        gbc.gridx = 0;
        gbc.gridy = 1;
        JLabel lexerLabel = new JLabel("Nombre Lexer:");
        lexerLabel.setForeground(new Color(0, 70, 140));
        inputPanel.add(lexerLabel, gbc);

        lexerNameField = new JTextField();
        gbc.gridx = 1;
        gbc.gridwidth = 2;
        inputPanel.add(lexerNameField, gbc);
        gbc.gridwidth = 1;

        // Botón para generar el Lexer
        generateButton = new JButton("Generar Lexer");
        generateButton.setBackground(new Color(100, 149, 237));
        generateButton.setForeground(Color.WHITE);
        gbc.gridx = 0;
        gbc.gridy = 2;
        gbc.gridwidth = 3;
        inputPanel.add(generateButton, gbc);
        gbc.gridwidth = 1;

        // Panel para salidas con pestañas: Texto y Visualización
        tabbedPane = new JTabbedPane();

        // Pestaña de salida de texto
        logArea = new JTextArea();
        logArea.setEditable(false);
        logArea.setFont(new Font("Monospaced", Font.PLAIN, 12));
        JScrollPane logScroll = new JScrollPane(logArea);
        tabbedPane.addTab("Salida de Texto", logScroll);

        // Pestaña para visualización de imagen
        JPanel imagePanel = new JPanel(new BorderLayout());
        imagePanel.setBackground(Color.WHITE);
        
        // Usamos ZoomableImagePanel para mostrar la imagen con zoom y pan
        zoomPanel = new ZoomableImagePanel();
        JScrollPane scrollPaneImage = new JScrollPane(zoomPanel);
        imagePanel.add(scrollPaneImage, BorderLayout.CENTER);

        // Slider para ajustar el zoom (25% a 400%)
        zoomSlider = new JSlider(JSlider.HORIZONTAL, 25, 400, 100);
        zoomSlider.setMajorTickSpacing(75);
        zoomSlider.setPaintTicks(true);
        zoomSlider.setPaintLabels(true);
        zoomSlider.addChangeListener(e -> {
            double scale = zoomSlider.getValue() / 100.0;
            zoomPanel.setScale(scale);
        });

        // Botón para refrescar la imagen
        refreshImageButton = new JButton("Refrescar Imagen");
        refreshImageButton.setBackground(new Color(60, 179, 113));
        refreshImageButton.setForeground(Color.WHITE);
        refreshImageButton.addActionListener(e -> loadGraphImage());

        // Panel inferior para el slider y el botón
        JPanel bottomPanel = new JPanel();
        bottomPanel.add(refreshImageButton);
        bottomPanel.add(new JLabel(" Zoom: "));
        bottomPanel.add(zoomSlider);
        imagePanel.add(bottomPanel, BorderLayout.SOUTH);

        tabbedPane.addTab("Visualización", imagePanel);

        // Agregar paneles al frame principal
        getContentPane().setLayout(new BorderLayout());
        getContentPane().add(inputPanel, BorderLayout.NORTH);
        getContentPane().add(tabbedPane, BorderLayout.CENTER);

        // Acciones de los botones
        browseButton.addActionListener(e -> chooseFile());
        generateButton.addActionListener(e -> generateLexer());
    }

    /**
     * Valida si una cadena es un identificador de clase Java válido.
     */
    private boolean isValidJavaIdentifier(String name) {
        if (name == null || name.isEmpty()) return false;
        // El primer carácter debe ser un JavaIdentifierStart
        if (!Character.isJavaIdentifierStart(name.charAt(0))) return false;
        // El resto deben ser JavaIdentifierPart
        for (int i = 1; i < name.length(); i++) {
            if (!Character.isJavaIdentifierPart(name.charAt(i))) {
                return false;
            }
        }
        return true;
    }

    /**
     * Muestra un JFileChooser para seleccionar el archivo YAL.
     */
    private void chooseFile() {
        JFileChooser fileChooser = new JFileChooser();
        int result = fileChooser.showOpenDialog(MainGUI.this);
        if (result == JFileChooser.APPROVE_OPTION) {
            File selectedFile = fileChooser.getSelectedFile();
            fileField.setText(selectedFile.getAbsolutePath());
        }
    }

    /**
     * Valida la entrada y ejecuta la generación del lexer en un hilo aparte.
     */
    private void generateLexer() {
        String archivoYal = fileField.getText().trim();
        String nombreLexer = lexerNameField.getText().trim();

        if (archivoYal.isEmpty()) {
            JOptionPane.showMessageDialog(this, "Ingresa el archivo YAL.", "Error", JOptionPane.ERROR_MESSAGE);
            return;
        }
        // Validar nombre de la clase
        if (!isValidJavaIdentifier(nombreLexer)) {
            JOptionPane.showMessageDialog(this,
                    "El nombre del lexer no es un identificador Java válido.\n" +
                    "Debe iniciar con letra o subrayado y solo contener letras, dígitos o subrayados.",
                    "Error",
                    JOptionPane.ERROR_MESSAGE);
            return;
        }

        // Limpiar salida de texto e imagen
        logArea.setText("");
        zoomPanel.setImage(null);

        // Ejecuta la generación en un hilo separado
        new Thread(() -> {
            // Capturamos tanto System.out como System.err en el mismo stream
            ByteArrayOutputStream baos = new ByteArrayOutputStream();
            PrintStream ps = new PrintStream(baos);
            PrintStream oldOut = System.out;
            PrintStream oldErr = System.err;

            try {
                // Redirigimos out y err
                System.setOut(ps);
                System.setErr(ps);

                // Lógica de generación (adaptada de Main.java)
                runLexerGeneration(archivoYal, nombreLexer);

            } catch (Exception ex) {
                ex.printStackTrace();
            } finally {
                // Restaurar out y err
                System.out.flush();
                System.err.flush();
                System.setOut(oldOut);
                System.setErr(oldErr);
            }

            // Mostramos en el logArea todo lo capturado
            String output = baos.toString();
            SwingUtilities.invokeLater(() -> logArea.setText(output));
        }).start();
    }

    /**
     * Contiene la lógica original para procesar el archivo YAL, construir AFN/AFD y generar el Lexer.
     */
    private void runLexerGeneration(String archivoYal, String nombreLexer) {
        try {
            // Paso 1: Parsear el archivo YALex
            YALexParser parser = new YALexParser();
            parser.parse(archivoYal);
            List<YALexParser.TokenRule> reglas = parser.getRules();
    
            // Paso 2: Construir un AFN por regla
            ThompsonConstructor thompson = new ThompsonConstructor();
            List<AFNCombiner.AFNToken> afns = new ArrayList<>();
            Map<Integer, String> acciones = new HashMap<>();
    
            for (int i = 0; i < reglas.size(); i++) {
                YALexParser.TokenRule regla = reglas.get(i);
                try {
                    String expandida = parser.expandirConjuntos(regla.regex);
                    System.out.println("Regla #" + (i + 1));
                    System.out.println("Original: " + regla.regex);
                    System.out.println("Expandida: " + expandida);
    
                    String regexLiteralExpandida = parser.expandirLiteralSiEsNecesario(expandida);
                    String regexPostfija = thompson.convertirPostfija(regexLiteralExpandida);
                    System.out.println("Postfija: " + regexPostfija);
    
                    AFN afn = thompson.construirDesdePostfijo(regexPostfija);
                    afns.add(new AFNCombiner.AFNToken(afn, regla.priority));
                    acciones.put(regla.priority, regla.action);
                } catch (Exception ex) {
                    System.err.println("Error en regla #" + (i + 1) + ": " + regla.regex);
                    ex.printStackTrace();
                    return;
                }
            }
    
            // Paso 3: Combinar AFNs
            AFNCombiner combinador = new AFNCombiner();
            AFN afnCombinado = combinador.combinarAFNs(afns);
    
            // Paso 4: Convertir a AFD
            AFDConstructor afdConstructor = new AFDConstructor();
            AFDConstructor.AFD afd = afdConstructor.convertirAFNtoAFD(afnCombinado);
    
            // Paso 5: Generar el Lexer Java
            GeneradorCodigoLexer.generarLexer(
                    nombreLexer,
                    afd,
                    acciones,
                    parser.getHeader(),
                    parser.getTrailer()
            );
    
            // Paso 6: Generar gráfica del AFD (archivo DOT)
            DFAGraph.generarDOT(afd, nombreLexer + "_AFD");
    
            // Convertir el archivo DOT a PNG usando Graphviz
            generateDotToPng(nombreLexer);
    
            // Paso 7: Probar el lexer con un archivo de entrada real
            System.out.println("\n🔍 Analizando archivo: prueba-complejidad-alta.txt");
            File testFile = new File("prueba-complejidad-alta.txt");
            if (testFile.exists()) {
                try {
                    String input = new String(Files.readAllBytes(testFile.toPath()));
                    System.out.println("\n Entrada:\n" + input);
                    System.out.println("\n Tokens reconocidos:");
                    // Compilar y ejecutar el lexer generado
                    String lexerJavaFile = "src/" + nombreLexer + ".java";
                    compileJavaFile(lexerJavaFile);
                    // Cargar la clase generada (se asume que está en el classpath)
                    Class<?> lexerClass = Class.forName(nombreLexer);
                    // Obtener el método getTokens(String) y ejecutarlo
                    java.lang.reflect.Method getTokensMethod = lexerClass.getMethod("getTokens", String.class);
                    getTokensMethod.invoke(null, input);
                } catch (Exception e) {
                    System.err.println("Error al ejecutar el lexer generado: " + e.getMessage());
                    e.printStackTrace();
                }
            } else {
                System.err.println("No se pudo leer el archivo de prueba: " + testFile.getAbsolutePath());
            }
        } catch (Exception e) {
            System.err.println("Error general: " + e.getMessage());
            e.printStackTrace();
        }
    }
    
    /**
     * Genera la imagen PNG a partir del archivo DOT utilizando Graphviz.
     * @param nombreLexer El nombre base del archivo DOT y PNG.
     */
    private void generateDotToPng(String nombreLexer) {
        // Si no deseas usar "dot" directamente, reemplaza "dot" con la ruta completa, por ejemplo "C:\\Program Files\\Graphviz\\bin\\dot.exe"
        String dotCommand = "dot"; 
        String dotFile = nombreLexer + "_AFD.dot";
        String pngFile = nombreLexer + "_AFD.png";
        
        try {
            Process process = Runtime.getRuntime().exec(new String[]{dotCommand, "-Tpng", dotFile, "-o", pngFile});
            int exitCode = process.waitFor();
            if (exitCode == 0) {
                System.out.println("Imagen PNG generada correctamente: " + pngFile);
            } else {
                System.err.println("Error al generar imagen PNG. Código de salida: " + exitCode);
            }
        } catch (IOException | InterruptedException e) {
            System.err.println("Error al generar imagen PNG: " + e.getMessage());
        }
    }
    
    /**
     * Compila un archivo Java utilizando el compilador del sistema.
     * @param filePath Ruta del archivo .java a compilar.
     */
    private void compileJavaFile(String filePath) throws IOException {
        javax.tools.JavaCompiler compiler = javax.tools.ToolProvider.getSystemJavaCompiler();
        int result = compiler.run(null, null, null, filePath);
        if (result != 0) {
            System.err.println("Error al compilar " + filePath);
        } else {
            System.out.println("Compilación exitosa de " + filePath);
        }
    }
    
    /**
     * Intenta cargar y mostrar la imagen generada del AFD.
     * Se espera que la imagen se guarde como "[nombreLexer]_AFD.png".
     */
    private void loadGraphImage() {
        String nombreLexer = lexerNameField.getText().trim();
        if (nombreLexer.isEmpty()) {
            zoomPanel.setImage(null);
            return;
        }
        String imagePath = nombreLexer + "_AFD.png";
        File imgFile = new File(imagePath);
        if (imgFile.exists()) {
            try {
                BufferedImage img = ImageIO.read(imgFile);
                zoomPanel.setImage(img);
                // Restablecer zoom a 100%
                zoomSlider.setValue(100);
            } catch (IOException ex) {
                System.err.println("Error al cargar la imagen: " + ex.getMessage());
                zoomPanel.setImage(null);
            }
        } else {
            System.err.println("Imagen no encontrada. Asegúrate de que se haya generado: " + imagePath);
            zoomPanel.setImage(null);
        }
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> {
            MainGUI gui = new MainGUI();
            gui.setVisible(true);
        });
    }

    /**
     * Panel personalizado para mostrar una imagen con capacidad de zoom.
     */
    class ZoomableImagePanel extends JPanel {
        private BufferedImage image;
        private double scale = 1.0; // Factor de escala inicial

        /**
         * Actualiza la imagen a mostrar.
         */
        public void setImage(BufferedImage img) {
            this.image = img;
            updatePreferredSize();
            repaint();
        }

        /**
         * Establece el factor de zoom.
         */
        public void setScale(double scale) {
            this.scale = scale;
            updatePreferredSize();
            repaint();
        }

        /**
         * Actualiza el tamaño preferido del panel en función de la imagen y la escala.
         */
        private void updatePreferredSize() {
            if (image != null) {
                int width = (int) (image.getWidth() * scale);
                int height = (int) (image.getHeight() * scale);
                setPreferredSize(new Dimension(width, height));
            } else {
                setPreferredSize(new Dimension(200, 200)); // Tamaño por defecto
            }
            revalidate();
        }

        @Override
        protected void paintComponent(Graphics g) {
            super.paintComponent(g);
            if (image != null) {
                Graphics2D g2 = (Graphics2D) g;
                g2.scale(scale, scale);
                g2.drawImage(image, 0, 0, this);
            }
        }
    }
}
