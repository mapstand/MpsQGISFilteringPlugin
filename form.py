from qgis.core import (
    QgsAction,
    QgsProject,
    QgsEditorWidgetSetup,
    QgsFieldConstraints,
    QgsRelation,
    QgsWkbTypes,
    QgsAttributeEditorContainer,
    QgsAttributeEditorRelation,
    QgsAttributeEditorField,
    QgsDefaultValue,
    QgsMapLayer,
    QgsVectorLayer,
    QgsDataSourceUri,
    QgsLayerTreeLayer,
)

from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLineEdit,
    QTextEdit,
    QPushButton,
    QLabel,
    QListWidget,
    QApplication,
    QGroupBox,
    QHBoxLayout,
)


class MapStandEditsFilteringDialog(QDialog):
    def __init__(self, iface, parent):
        super().__init__()
        self.init_ui()

    @property
    def _layers(self):

        return [
            layer
            for layer in QgsProject.instance().mapLayers().values()
            if layer.type() == QgsMapLayer.VectorLayer
        ]

    @property
    def _project_instance(self):
        return QgsProject.instance()

    @property
    def _project_instance_custom_variables(self):
        return self._project_instance.customVariables()

    @property
    def _stored_editing_filters(self):
        return self._project_instance_custom_variables.pop("editing_filters", {})

    @property
    def _filterable_fields(self):

        return sorted(
            list(
                set(
                    [field.name() for layer in self._layers for field in layer.fields()]
                )
            )
        )

    @property
    def _frame_style(self):
        return "QGroupBox { border: 1px solid #000; padding: 20px; margin-top: 10px}"

    @property
    def _selected_filters(self):

        return [
            self.existing_filter_list.item(item_index).text()
            for item_index in range(self.existing_filter_list.count())
            if self.existing_filter_list.item(item_index).isSelected()
        ]

    @property
    def _selected_filtered_fields(self):
        return [
            self.txt_list_selected_fields.item(item_index).text()
            for item_index in range(self.txt_list_selected_fields.count())
        ]

    def update_existing_filter_list(self):
        self.existing_filter_list.clear()

        for _ in self._stored_editing_filters.keys():
            self.existing_filter_list.addItem(_)

    def init_ui(self):
        
        self.setWindowTitle("MapStand Edits Filtering")

        self.layout_main = QHBoxLayout()

        layout_existing = QVBoxLayout()
        group_existing = QGroupBox("Existing Filters")
        group_existing.setStyleSheet(self._frame_style)
        group_existing.setLayout(layout_existing)

        self.existing_filter_list = QListWidget()
        self.existing_filter_list.itemDoubleClicked.connect(
            self.action_load_filter_configuration_from_project
        )
        self.existing_filter_list.setSelectionMode(QListWidget.MultiSelection)
        self.update_existing_filter_list()

        btn_filters_apply = QPushButton("Apply Selected")
        btn_filters_apply.clicked.connect(self.action_filters_apply)

        btn_filters_delete = QPushButton("Delete Selected")
        btn_filters_delete.clicked.connect(self.action_filters_delete)

        layout_existing.addWidget(QLabel("Double-click an existing filter to edit"))
        layout_existing.addWidget(self.existing_filter_list)
        layout_existing.addWidget(btn_filters_apply)
        layout_existing.addWidget(btn_filters_delete)

        self.layout_main.addWidget(group_existing)

        layout_editing = QHBoxLayout()
        group_editing = QGroupBox("Filter Editing")
        group_editing.setStyleSheet(self._frame_style)
        group_editing.setLayout(layout_editing)

        layout_fields_selection = QVBoxLayout() 
        layout_query_params = QVBoxLayout()

        group_fields_selection = QGroupBox("Filter Fields")
        group_fields_selection.setStyleSheet(self._frame_style)
        group_fields_selection.setLayout(layout_fields_selection)

        self.txt_search_filterable_fields = QLineEdit()
        self.txt_search_filterable_fields.setPlaceholderText(
            "Search for fields to filter"
        )
        self.txt_search_filterable_fields.textChanged.connect(
            self.action_search_filterable_fields
        )

        self.txt_list_searched_fields = QListWidget()
        self.txt_list_searched_fields.itemClicked.connect(
            self.action_add_selected_field
        )

        self.txt_list_selected_fields = QListWidget()
        self.txt_list_selected_fields.itemClicked.connect(
            self.action_remove_selected_field
        )

        layout_fields_selection.addWidget(self.txt_search_filterable_fields)
        layout_fields_selection.addWidget(self.txt_list_searched_fields)
        layout_fields_selection.addWidget(self.txt_list_selected_fields)

        group_query_params = QGroupBox("Filter Value")
        group_query_params.setStyleSheet(self._frame_style)

        self.txt_filter_condition = QTextEdit()
        self.txt_filter_condition.setPlaceholderText("Add filter text")

        self.txt_filter_name = QLineEdit()
        self.txt_filter_name.setPlaceholderText("Filter name")

        btn_filter_save = QPushButton("Save")
        btn_filter_save.clicked.connect(self.action_save_filter)

        layout_query_params.addWidget(self.txt_filter_condition)
        layout_query_params.addWidget(self.txt_filter_name)
        layout_query_params.addWidget(btn_filter_save)

        group_query_params.setLayout(layout_query_params)

        layout_editing.addWidget(group_fields_selection)
        layout_editing.addWidget(group_query_params)

        self.layout_main.addWidget(group_editing)

        self.setLayout(self.layout_main)

    def clear_parameter_widgets(self):
        self.txt_filter_condition.clear()
        self.txt_filter_name.clear()
        self.txt_search_filterable_fields.clear()
        self.txt_list_selected_fields.clear()

    def action_save_filter(self):
        self.save_filter_configuration_to_qgis_project()
        self.clear_parameter_widgets()

    def action_load_filter_configuration_from_project(self, item):

        filter_name = item.text()
        custom_variables = self._project_instance_custom_variables
        filter_variable = custom_variables.pop("editing_filters", {})
        filter_item = filter_variable.pop(filter_name, {})

        self.txt_filter_name.setText(filter_name)
        self.txt_list_selected_fields.clear()

        for item in filter_item["selected_fields"]:
            self.txt_list_selected_fields.addItem(item)

        self.txt_filter_condition.clear()
        self.txt_list_searched_fields.clear()
        self.txt_filter_condition.setText(filter_item["query_condition"])

    def action_filters_delete(self):

        self.remove_filters_from_layers()
        custom_variables = self._project_instance_custom_variables
        filter_variable = custom_variables.pop("editing_filters", {})
        for filter_name in self._selected_filters:
            filter_item = filter_variable.pop(filter_name, {})
        custom_variables["editing_filters"] = filter_variable
        self._project_instance.setCustomVariables(custom_variables)
        self.txt_list_searched_fields.clear()
        self.txt_list_selected_fields.clear()
        self.txt_filter_condition.clear()
        self.update_existing_filter_list()

    def save_filter_configuration_to_qgis_project(self):

        filter_name = self.txt_filter_name.text()
        custom_variables = self._project_instance_custom_variables
        filter_variable = custom_variables.pop("editing_filters", {})
        filter_item = filter_variable.pop(filter_name, {})
        filter_item["selected_fields"] = self._selected_filtered_fields
        filter_item["query_condition"] = self.txt_filter_condition.toPlainText()
        filter_variable[filter_name] = filter_item
        custom_variables["editing_filters"] = filter_variable
        self._project_instance.setCustomVariables(custom_variables)
        self.update_existing_filter_list()

    def remove_filters_from_layers(self):
        for layer in self._layers:
            partial_expressions = layer.subsetString().split("\n")
            skip_expression = False
            updated_partial_expressions = []

            for partial_expression in partial_expressions:

                if partial_expression.startswith("-- AUTOFILTER: "):
                    skip_expression = True

                if skip_expression == False:
                    updated_partial_expressions.append(partial_expression)

            layer.setSubsetString("\n".join(updated_partial_expressions))

    def add_filters_to_layers(self):

        custom_variables = self._project_instance_custom_variables

        filter_variable = custom_variables.pop("editing_filters", {})

        for filter_name in self._selected_filters:

            filter_data = filter_variable[filter_name]

            expression = filter_data["query_condition"]
            selected_fields = filter_data["selected_fields"]

            for layer in self._layers:

                layer_field_names = [field.name() for field in layer.fields()]

                partial_expressions = layer.subsetString().split("\n")

                filter_name_tag = f"-- AUTOFILTER: {filter_name}"

                sub_queries = []

                for selected_field_name in selected_fields:
                    if selected_field_name in layer_field_names:
                        encased_field_name = f'"{selected_field_name}"'
                        sub_queries.append(f"{encased_field_name} {expression}")

                update_expression = " OR ".join(sub_queries)

                if update_expression != "":

                    update_expression = f'( {" OR ".join(sub_queries)} )'

                    if len(partial_expressions) == 1 and partial_expressions[0] == "":
                        partial_expressions[0] = filter_name_tag
                        partial_expressions.append(update_expression)
                    else:
                        partial_expressions.append(filter_name_tag)
                        partial_expressions.append(f"AND {update_expression}")

                    layer.setSubsetString("\n".join(partial_expressions))

    def action_filters_apply(self):

        self.remove_filters_from_layers()
        self.add_filters_to_layers()

    def action_search_filterable_fields(self):

        self.txt_list_searched_fields.clear()

        text = self.txt_search_filterable_fields.text()

        if text:
            filtered_fields = [
                field_name
                for field_name in self._filterable_fields
                if text in field_name
            ]

            for filtered_field_name in filtered_fields:
                self.txt_list_searched_fields.addItem(filtered_field_name)

    def action_add_selected_field(self, item):
        selected_text = item.text()

        if selected_text not in self._selected_filtered_fields:
            self.txt_list_selected_fields.addItem(selected_text)

    def action_remove_selected_field(self, item):
        self.txt_list_selected_fields.takeItem(self.txt_list_selected_fields.row(item))
