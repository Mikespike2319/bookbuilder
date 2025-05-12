import sys
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                              QLabel, QPushButton, QTextEdit, QComboBox, 
                              QDoubleSpinBox, QFileDialog, QMessageBox, 
                              QTabWidget, QHBoxLayout, QProgressBar, QLineEdit,
                              QListWidget, QListWidgetItem, QInputDialog, QDialog,
                              QFormLayout, QDialogButtonBox)
from PySide6.QtCore import QThread, Signal
import json
from core.ai_assist import generate_outline, generate_chapter_from_outline, reset_current_chapter, get_memory_context
from core.nlp_extract import extract_entities_from_chapter, update_memory_with_entities

# Worker thread for background processing
class GenerateWorker(QThread):
    finished = Signal(str)
    progress = Signal(str)
    error = Signal(str)
    
    def __init__(self, task_type, params):
        super().__init__()
        self.task_type = task_type
        self.params = params
        
    def run(self):
        try:
            if self.task_type == "outline":
                self.progress.emit("Generating outline...")
                result = generate_outline(
                    self.params["prompt"],
                    genre=self.params["genre"],
                    model=self.params["model"],
                    temperature=self.params["temperature"]
                )
                self.finished.emit(result)
                
            elif self.task_type == "chapter":
                self.progress.emit("Generating chapter...")
                result = generate_chapter_from_outline(
                    self.params["outline"],
                    model=self.params["model"],
                    temperature=self.params["temperature"],
                    min_words=3000
                )
                self.finished.emit(result)
                
            elif self.task_type == "analyze":
                self.progress.emit("Analyzing chapter...")
                characters, locations = extract_entities_from_chapter(self.params["file_path"])
                result = f"Characters Found: {characters}\n\nLocations Found: {locations}"
                self.finished.emit(result)
                
        except Exception as e:
            self.error.emit(f"Error: {str(e)}")


class MemoryViewerTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.load_memory_data()
        
    def init_ui(self):
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # Create tab widget for characters and locations
        self.memory_tabs = QTabWidget()
        
        # Characters tab
        self.characters_widget = QWidget()
        characters_layout = QVBoxLayout(self.characters_widget)
        
        self.characters_list = QListWidget()
        
        characters_btn_layout = QHBoxLayout()
        self.add_character_btn = QPushButton("Add Character")
        self.edit_character_btn = QPushButton("Edit Character")
        self.delete_character_btn = QPushButton("Delete Character")
        
        characters_btn_layout.addWidget(self.add_character_btn)
        characters_btn_layout.addWidget(self.edit_character_btn)
        characters_btn_layout.addWidget(self.delete_character_btn)
        
        characters_layout.addWidget(self.characters_list)
        characters_layout.addLayout(characters_btn_layout)
        
        # Locations tab
        self.locations_widget = QWidget()
        locations_layout = QVBoxLayout(self.locations_widget)
        
        self.locations_list = QListWidget()
        
        locations_btn_layout = QHBoxLayout()
        self.add_location_btn = QPushButton("Add Location")
        self.edit_location_btn = QPushButton("Edit Location")
        self.delete_location_btn = QPushButton("Delete Location")
        
        locations_btn_layout.addWidget(self.add_location_btn)
        locations_btn_layout.addWidget(self.edit_location_btn)
        locations_btn_layout.addWidget(self.delete_location_btn)
        
        locations_layout.addWidget(self.locations_list)
        locations_layout.addLayout(locations_btn_layout)
        
        # Add tabs to tab widget
        self.memory_tabs.addTab(self.characters_widget, "Characters")
        self.memory_tabs.addTab(self.locations_widget, "Locations")
        
        # Add tab widget to main layout
        main_layout.addWidget(self.memory_tabs)
        
        # Connect signals
        self.add_character_btn.clicked.connect(lambda: self.add_item("character"))
        self.edit_character_btn.clicked.connect(lambda: self.edit_item("character"))
        self.delete_character_btn.clicked.connect(lambda: self.delete_item("character"))
        
        self.add_location_btn.clicked.connect(lambda: self.add_item("location"))
        self.edit_location_btn.clicked.connect(lambda: self.edit_item("location"))
        self.delete_location_btn.clicked.connect(lambda: self.delete_item("location"))
        
    def load_memory_data(self):
        """Load character and location data from memory files"""
        memory_context = get_memory_context()
        
        # Clear existing items
        self.characters_list.clear()
        self.locations_list.clear()
        
        # Add characters
        for character in memory_context.get("characters", []):
            self.characters_list.addItem(character)
            
        # Add locations
        for location in memory_context.get("locations", []):
            self.locations_list.addItem(location)
    
    def add_item(self, item_type):
        """Add a new character or location"""
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Add {item_type.capitalize()}")
        
        layout = QFormLayout(dialog)
        name_input = QLineEdit()
        layout.addRow(f"{item_type.capitalize()} Name:", name_input)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec() == QDialog.Accepted:
            name = name_input.text().strip()
            if name:
                if item_type == "character":
                    self.characters_list.addItem(name)
                else:
                    self.locations_list.addItem(name)
                self.save_memory_data()
    
    def edit_item(self, item_type):
        """Edit a selected character or location"""
        if item_type == "character":
            current_item = self.characters_list.currentItem()
            list_widget = self.characters_list
        else:
            current_item = self.locations_list.currentItem()
            list_widget = self.locations_list
            
        if not current_item:
            QMessageBox.warning(self, "Selection Required", f"Please select a {item_type} to edit.")
            return
            
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Edit {item_type.capitalize()}")
        
        layout = QFormLayout(dialog)
        name_input = QLineEdit(current_item.text())
        layout.addRow(f"{item_type.capitalize()} Name:", name_input)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec() == QDialog.Accepted:
            name = name_input.text().strip()
            if name:
                current_item.setText(name)
                self.save_memory_data()
    
    def delete_item(self, item_type):
        """Delete a selected character or location"""
        if item_type == "character":
            current_item = self.characters_list.currentItem()
            list_widget = self.characters_list
        else:
            current_item = self.locations_list.currentItem()
            list_widget = self.locations_list
            
        if not current_item:
            QMessageBox.warning(self, "Selection Required", f"Please select a {item_type} to delete.")
            return
            
        reply = QMessageBox.question(
            self, 
            "Confirm Deletion", 
            f"Are you sure you want to delete '{current_item.text()}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            row = list_widget.row(current_item)
            list_widget.takeItem(row)
            self.save_memory_data()
    
    def save_memory_data(self):
        """Save character and location data to memory files"""
        memory_dir = "memory"
        
        # Save characters
        characters = []
        for i in range(self.characters_list.count()):
            characters.append(self.characters_list.item(i).text())
            
        char_path = os.path.join(memory_dir, "characters.json")
        with open(char_path, "w") as f:
            json.dump(characters, f, indent=2)
            
        # Save locations
        locations = []
        for i in range(self.locations_list.count()):
            locations.append(self.locations_list.item(i).text())
            
        loc_path = os.path.join(memory_dir, "locations.json")
        with open(loc_path, "w") as f:
            json.dump(locations, f, indent=2)
            
        QMessageBox.information(self, "Success", "Memory data saved successfully.")


class NovelAssistantGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Ensure directories exist
        os.makedirs("chapters", exist_ok=True)
        os.makedirs("memory", exist_ok=True)
        
        self.setWindowTitle("Novel Assistant")
        self.setMinimumSize(800, 600)
        
        self.current_outline = ""
        self.current_chapter = ""
        self.current_file_path = ""
        self.worker = None  # Initialize worker to None
        
        self.init_ui()
        
    def init_ui(self):
        # Main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        
        # Story continuity controls
        continuity_layout = QHBoxLayout()
        continuity_label = QLabel("Story Mode:")
        self.new_book_btn = QPushButton("New Book")
        self.continue_story_btn = QPushButton("Continue Story")
        
        # Style the buttons
        self.new_book_btn.setStyleSheet("background-color: #f0ad4e; font-weight: bold;")
        self.continue_story_btn.setStyleSheet("background-color: #5bc0de; font-weight: bold;")
        
        continuity_layout.addWidget(continuity_label)
        continuity_layout.addWidget(self.new_book_btn)
        continuity_layout.addWidget(self.continue_story_btn)
        continuity_layout.addStretch()
        
        # Create tab widget for main application
        self.main_tabs = QTabWidget()
        
        # Create generator tab (existing functionality)
        self.generator_tab = QWidget()
        generator_layout = QVBoxLayout(self.generator_tab)
        
        # Input section
        input_layout = QVBoxLayout()
        
        # Prompt row
        prompt_layout = QHBoxLayout()
        prompt_label = QLabel("Prompt:")
        self.prompt_input = QLineEdit()
        prompt_layout.addWidget(prompt_label)
        prompt_layout.addWidget(self.prompt_input)
        
        # Genre and Temperature row
        genre_temp_layout = QHBoxLayout()
        
        genre_label = QLabel("Genre:")
        self.genre_combo = QComboBox()
        self.genre_combo.addItems(["Fantasy", "Science Fiction", "Mystery", "Romance", "Horror", "Historical", "Adventure"])
        
        temp_label = QLabel("Temperature:")
        self.temp_spin = QDoubleSpinBox()
        self.temp_spin.setRange(0.0, 1.0)
        self.temp_spin.setSingleStep(0.1)
        self.temp_spin.setValue(0.7)
        
        genre_temp_layout.addWidget(genre_label)
        genre_temp_layout.addWidget(self.genre_combo)
        genre_temp_layout.addStretch()
        genre_temp_layout.addWidget(temp_label)
        genre_temp_layout.addWidget(self.temp_spin)
        
        # Model row
        model_layout = QHBoxLayout()
        model_label = QLabel("Model:")
        self.model_combo = QComboBox()
        self.model_combo.addItems(["gpt-4", "gpt-3.5-turbo"])
        
        model_layout.addWidget(model_label)
        model_layout.addWidget(self.model_combo)
        model_layout.addStretch()
        
        # Button row
        button_layout = QHBoxLayout()
        self.generate_outline_btn = QPushButton("Generate Outline")
        self.generate_chapter_btn = QPushButton("Generate Chapter")
        self.save_chapter_btn = QPushButton("Save Chapter")
        
        button_layout.addWidget(self.generate_outline_btn)
        button_layout.addWidget(self.generate_chapter_btn)
        button_layout.addWidget(self.save_chapter_btn)  # Add to button_layout, not layout
        
        # Remove this duplicate line:
        button_layout.addWidget(self.generate_chapter_btn)
        
        # Add all input layouts
        input_layout.addLayout(prompt_layout)
        input_layout.addLayout(genre_temp_layout)
        input_layout.addLayout(model_layout)
        input_layout.addLayout(button_layout)
        
        # Output section
        output_layout = QVBoxLayout()
        output_label = QLabel("Output Preview:")
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%v%")
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        
        # Action buttons
        action_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save to File")
        self.analyze_btn = QPushButton("Analyze Chapter")
        self.load_btn = QPushButton("Load File")
        
        action_layout.addWidget(self.save_btn)
        action_layout.addWidget(self.analyze_btn)
        action_layout.addWidget(self.load_btn)
        
        # Add output components
        output_layout.addWidget(output_label)
        output_layout.addWidget(self.output_text)
        output_layout.addWidget(self.progress_bar)
        output_layout.addLayout(action_layout)
        
        # Add all to generator tab layout
        generator_layout.addLayout(input_layout)
        generator_layout.addLayout(output_layout)
        
        # Create memory viewer tab
        self.memory_tab = MemoryViewerTab()
        
        # Add tabs to main tab widget
        self.main_tabs.addTab(self.generator_tab, "Generator")
        self.main_tabs.addTab(self.memory_tab, "Memory Viewer")
        
        # Add main tab widget to layout
        main_layout.addLayout(continuity_layout)
        main_layout.addWidget(self.main_tabs)
        
        # Set the main widget
        self.setCentralWidget(main_widget)
        
        # Connect signals
        self.generate_outline_btn.clicked.connect(self.on_generate_outline)
        self.generate_chapter_btn.clicked.connect(self.on_generate_chapter)
        self.save_btn.clicked.connect(self.on_save_file)
        self.analyze_btn.clicked.connect(self.on_analyze_chapter)
        self.load_btn.clicked.connect(self.on_load_file)
        self.save_chapter_btn.clicked.connect(self.save_chapter)  # Add this line
        
    def on_generate_outline(self):
        prompt = self.prompt_input.text().strip()
        if not prompt:
            QMessageBox.warning(self, "Input Required", "Please enter a prompt for your chapter.")
            return
            
        # Prepare parameters
        params = {
            "prompt": prompt,
            "genre": self.genre_combo.currentText().lower(),
            "model": self.model_combo.currentText(),
            "temperature": self.temp_spin.value()
        }
        
        # Start worker thread
        self.worker = GenerateWorker("outline", params)
        self.worker.finished.connect(self.on_outline_generated)
        self.worker.progress.connect(self.update_progress)
        self.worker.error.connect(self.show_error)
        
        # Update UI
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.output_text.setText("Generating outline...")
        self.disable_inputs(True)
        
        # Start generation
        self.worker.start()
        
    def on_outline_generated(self, outline):
        self.current_outline = outline
        self.output_text.setText(outline)
        self.progress_bar.setValue(100)
        self.disable_inputs(False)
        
    def on_generate_chapter(self):
        if not self.current_outline:
            # Check if there's text in the output that could be used as an outline
            outline = self.output_text.toPlainText().strip()
            if not outline:
                QMessageBox.warning(self, "Outline Required", 
                                   "Please generate an outline first or load an outline file.")
                return
            self.current_outline = outline
            
        # Prepare parameters
        params = {
            "outline": self.current_outline,
            "model": self.model_combo.currentText(),
            "temperature": self.temp_spin.value()
        }
        
        # Start worker thread
        self.worker = GenerateWorker("chapter", params)
        self.worker.finished.connect(self.on_chapter_generated)
        self.worker.progress.connect(self.update_progress)
        self.worker.error.connect(self.show_error)
        
        # Update UI
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.output_text.setText("Generating chapter... This may take a few minutes.")
        self.disable_inputs(True)
        
        # Start generation
        self.worker.start()
        
    def on_chapter_generated(self, chapter):
        self.current_chapter = chapter
        self.output_text.setText(chapter)
        self.progress_bar.setValue(100)
        self.disable_inputs(False)
        
    def on_save_file(self):
        content = self.output_text.toPlainText()
        if not content:
            QMessageBox.warning(self, "No Content", "There is no content to save.")
            return
            
        # Determine default file type based on content
        default_suffix = "_chapter.md" if self.current_chapter else "_outline.md"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Save File", 
            os.path.join("chapters", f"new{default_suffix}"),
            "Markdown Files (*.md);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    f.write(content)
                QMessageBox.information(self, "Success", f"File saved successfully to {file_path}")
                self.current_file_path = file_path
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save file: {str(e)}")
                
    def on_analyze_chapter(self):
        # If we have a current file path, use it
        if self.current_file_path and os.path.exists(self.current_file_path):
            self.analyze_file(self.current_file_path)
        else:
            # Otherwise, prompt to select a file
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Select Chapter to Analyze",
                "chapters",
                "Markdown Files (*.md);;All Files (*)"
            )
            
            if file_path:
                self.analyze_file(file_path)
                
    def analyze_file(self, file_path):
        # Prepare parameters
        params = {
            "file_path": file_path
        }
        
        # Start worker thread
        self.worker = GenerateWorker("analyze", params)
        self.worker.finished.connect(self.on_analysis_complete)
        self.worker.progress.connect(self.update_progress)
        self.worker.error.connect(self.show_error)
        
        # Update UI
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.output_text.setText(f"Analyzing {os.path.basename(file_path)}...")
        self.disable_inputs(True)
        
        # Start analysis
        self.worker.start()
        
    def on_analysis_complete(self, result):
        self.output_text.setText(result)
        self.progress_bar.setValue(100)
        self.disable_inputs(False)
        
        # Refresh memory viewer tab
        self.memory_tab.load_memory_data()
        
    def on_load_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open File",
            "chapters",
            "Markdown Files (*.md);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                self.output_text.setText(content)
                self.current_file_path = file_path
                
                # Determine if this is an outline or chapter
                if "_outline" in file_path:
                    self.current_outline = content
                else:
                    self.current_chapter = content
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load file: {str(e)}")
                
    def save_chapter(self):
        """Save the current chapter with automatic numbering"""
        if not self.current_chapter:
            QMessageBox.warning(self, "No Content", "There is no chapter to save.")
            return
        
        try:
            from core.ai_assist import save_new_chapter, append_to_current
            # Save as individual chapter file
            chapter_path = save_new_chapter(self.current_chapter)
            # Also append to current story
            current_file = append_to_current(self.current_chapter)
        
            QMessageBox.information(
                self, 
                "Success", 
                f"Chapter saved as {os.path.basename(chapter_path)} "
                f"and appended to current story."
            )
            self.current_file_path = chapter_path
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save chapter: {str(e)}")
        
    def update_progress(self, message: str):
        """Update the progress display with a message"""
        self.output_text.append(f"[Progress] {message}")
        
    def show_error(self, error_message: str):
        """Display an error message"""
        QMessageBox.critical(self, "Error", error_message)
        self.progress_bar.setVisible(False)
        self.disable_inputs(False)
        
    def disable_inputs(self, disabled: bool):
        """Enable or disable input controls during processing"""
        self.prompt_input.setDisabled(disabled)
        self.genre_combo.setDisabled(disabled)
        self.temp_spin.setDisabled(disabled)
        self.model_combo.setDisabled(disabled)
        self.generate_outline_btn.setDisabled(disabled)
        self.generate_chapter_btn.setDisabled(disabled)
        self.save_btn.setDisabled(disabled)
        self.analyze_btn.setDisabled(disabled)
        self.load_btn.setDisabled(disabled)
        self.save_chapter_btn.setDisabled(disabled)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NovelAssistantGUI()
    window.show()
    sys.exit(app.exec())


# Add to init_ui method:
self.book_title_input = QLineEdit("My Novel")
layout.addWidget(QLabel("Book Title:"))
layout.addWidget(self.book_title_input)

# Then modify save_chapter method:
def save_chapter(self):
    """Save the current chapter with automatic numbering"""
    if not self.current_chapter:
        QMessageBox.warning(self, "No Content", "There is no chapter to save.")
        return
    
    try:
        # Save to next chapter file
        from core.ai_assist import save_new_chapter, append_to_current
        
        # Save as individual chapter file
        chapter_path = save_new_chapter(self.current_chapter)
        
        # Also append to current story
        current_file = append_to_current(self.current_chapter)
        
        QMessageBox.information(
            self, 
            "Success", 
            f"Chapter saved as {os.path.basename(chapter_path)} and appended to current story."
        )
        self.current_file_path = chapter_path
    except Exception as e:
        QMessageBox.critical(self, "Error", f"Failed to save chapter: {str(e)}")


def update_progress(self, message: str):
    """Update the progress display with a message"""
    self.output_text.append(f"[Progress] {message}")
    
def show_error(self, error_message: str):
    """Display an error message"""
    QMessageBox.critical(self, "Error", error_message)
    self.progress_bar.setVisible(False)
    self.disable_inputs(False)


# In the init_ui method, add:
self.new_book_btn.clicked.connect(self.on_new_book)
self.continue_story_btn.clicked.connect(self.on_continue_story)

# Add this method to the NovelAssistantGUI class
def on_continue_story(self):
    """Continue the current story by loading previous context"""
    try:
        # Check if we have a current story
        current_file = os.path.join("memory", "current_chapter.txt")
        
        if not os.path.exists(current_file) or os.path.getsize(current_file) == 0:
            QMessageBox.information(
                self,
                "No Story Found",
                "No existing story found. Please start a new book first."
            )
            return
            
        # Load the current story
        with open(current_file, "r", encoding="utf-8") as f:
            current_story = f.read()
            
        # Show the current story in the output
        self.output_text.setText(f"Continuing from existing story ({len(current_story.split())} words)...\n\n{current_story[:500]}...\n\n[Story continues]")
        
        # Ask for a continuation prompt
        prompt, ok = QInputDialog.getText(
            self,
            "Continue Story",
            "Enter a prompt for the next chapter:"
        )
        
        if ok and prompt:
            # Generate a new outline based on the current story
            self.prompt_input.setText(prompt)
            
            # Prepare parameters with context from current story
            params = {
                "prompt": f"Continue this story: {current_story[-1000:]}... {prompt}",
                "genre": self.genre_combo.currentText().lower(),
                "model": self.model_combo.currentText(),
                "temperature": self.temp_spin.value()
            }
            
            # Start worker thread for outline
            self.worker = GenerateWorker("outline", params)
            self.worker.finished.connect(self.on_outline_generated)
            self.worker.progress.connect(self.update_progress)
            self.worker.error.connect(self.show_error)
            
            # Update UI
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            self.output_text.setText("Generating continuation outline...")
            self.disable_inputs(True)
            
            # Start generation
            self.worker.start()
    except Exception as e:
        QMessageBox.critical(self, "Error", f"Failed to continue story: {str(e)}")

# Add this method to handle new book creation
def on_new_book(self):
    """Start a new book by resetting the current chapter"""
    reply = QMessageBox.question(
        self,
        "New Book",
        "Are you sure you want to start a new book? This will reset the current story.",
        QMessageBox.Yes | QMessageBox.No,
        QMessageBox.No
    )
    
    if reply == QMessageBox.Yes:
        try:
            from core.ai_assist import reset_current_chapter
            reset_current_chapter()
            self.output_text.setText("Started a new book. Enter a prompt and generate an outline to begin.")
            self.current_outline = ""
            self.current_chapter = ""
            self.current_file_path = ""
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to start new book: {str(e)}")