import sys
from antlr4 import *
from saapy.antlr.tsql.autogen import tsqlLexer, tsqlParser, tsqlListener


class TsqlPrinter(tsqlListener):
    def __init__(self):
        pass
        
    # def enterEveryRule(self, ctx):
#
#         print(ctx)
        
    # Enter a parse tree produced by tsqlParser#tsql_file.
    def enterTsql_file(self, ctx:tsqlParser.Tsql_fileContext):
        print('enter tsql_file')

    # Exit a parse tree produced by tsqlParser#tsql_file.
    def exitTsql_file(self, ctx:tsqlParser.Tsql_fileContext):
        print('exit tsql_file')

    # Enter a parse tree produced by tsqlParser#sql_clauses.
    def enterSql_clauses(self, ctx:tsqlParser.Sql_clausesContext):
        pass

    # Exit a parse tree produced by tsqlParser#sql_clauses.
    def exitSql_clauses(self, ctx:tsqlParser.Sql_clausesContext):
        pass


    # Enter a parse tree produced by tsqlParser#sql_clause.
    def enterSql_clause(self, ctx:tsqlParser.Sql_clauseContext):
        pass

    # Exit a parse tree produced by tsqlParser#sql_clause.
    def exitSql_clause(self, ctx:tsqlParser.Sql_clauseContext):
        pass


    # Enter a parse tree produced by tsqlParser#dml_clause.
    def enterDml_clause(self, ctx:tsqlParser.Dml_clauseContext):
        pass

    # Exit a parse tree produced by tsqlParser#dml_clause.
    def exitDml_clause(self, ctx:tsqlParser.Dml_clauseContext):
        pass


    # Enter a parse tree produced by tsqlParser#ddl_clause.
    def enterDdl_clause(self, ctx:tsqlParser.Ddl_clauseContext):
        pass

    # Exit a parse tree produced by tsqlParser#ddl_clause.
    def exitDdl_clause(self, ctx:tsqlParser.Ddl_clauseContext):
        pass


    # Enter a parse tree produced by tsqlParser#block_statement.
    def enterBlock_statement(self, ctx:tsqlParser.Block_statementContext):
        pass

    # Exit a parse tree produced by tsqlParser#block_statement.
    def exitBlock_statement(self, ctx:tsqlParser.Block_statementContext):
        pass


    # Enter a parse tree produced by tsqlParser#break_statement.
    def enterBreak_statement(self, ctx:tsqlParser.Break_statementContext):
        pass

    # Exit a parse tree produced by tsqlParser#break_statement.
    def exitBreak_statement(self, ctx:tsqlParser.Break_statementContext):
        pass


    # Enter a parse tree produced by tsqlParser#continue_statement.
    def enterContinue_statement(self, ctx:tsqlParser.Continue_statementContext):
        pass

    # Exit a parse tree produced by tsqlParser#continue_statement.
    def exitContinue_statement(self, ctx:tsqlParser.Continue_statementContext):
        pass


    # Enter a parse tree produced by tsqlParser#goto_statement.
    def enterGoto_statement(self, ctx:tsqlParser.Goto_statementContext):
        pass

    # Exit a parse tree produced by tsqlParser#goto_statement.
    def exitGoto_statement(self, ctx:tsqlParser.Goto_statementContext):
        pass


    # Enter a parse tree produced by tsqlParser#if_statement.
    def enterIf_statement(self, ctx:tsqlParser.If_statementContext):
        pass

    # Exit a parse tree produced by tsqlParser#if_statement.
    def exitIf_statement(self, ctx:tsqlParser.If_statementContext):
        pass


    # Enter a parse tree produced by tsqlParser#return_statement.
    def enterReturn_statement(self, ctx:tsqlParser.Return_statementContext):
        pass

    # Exit a parse tree produced by tsqlParser#return_statement.
    def exitReturn_statement(self, ctx:tsqlParser.Return_statementContext):
        pass


    # Enter a parse tree produced by tsqlParser#throw_statement.
    def enterThrow_statement(self, ctx:tsqlParser.Throw_statementContext):
        pass

    # Exit a parse tree produced by tsqlParser#throw_statement.
    def exitThrow_statement(self, ctx:tsqlParser.Throw_statementContext):
        pass


    # Enter a parse tree produced by tsqlParser#try_catch_statement.
    def enterTry_catch_statement(self, ctx:tsqlParser.Try_catch_statementContext):
        pass

    # Exit a parse tree produced by tsqlParser#try_catch_statement.
    def exitTry_catch_statement(self, ctx:tsqlParser.Try_catch_statementContext):
        pass


    # Enter a parse tree produced by tsqlParser#waitfor_statement.
    def enterWaitfor_statement(self, ctx:tsqlParser.Waitfor_statementContext):
        pass

    # Exit a parse tree produced by tsqlParser#waitfor_statement.
    def exitWaitfor_statement(self, ctx:tsqlParser.Waitfor_statementContext):
        pass


    # Enter a parse tree produced by tsqlParser#while_statement.
    def enterWhile_statement(self, ctx:tsqlParser.While_statementContext):
        pass

    # Exit a parse tree produced by tsqlParser#while_statement.
    def exitWhile_statement(self, ctx:tsqlParser.While_statementContext):
        pass


    # Enter a parse tree produced by tsqlParser#print_statement.
    def enterPrint_statement(self, ctx:tsqlParser.Print_statementContext):
        pass

    # Exit a parse tree produced by tsqlParser#print_statement.
    def exitPrint_statement(self, ctx:tsqlParser.Print_statementContext):
        pass


    # Enter a parse tree produced by tsqlParser#raiseerror_statement.
    def enterRaiseerror_statement(self, ctx:tsqlParser.Raiseerror_statementContext):
        pass

    # Exit a parse tree produced by tsqlParser#raiseerror_statement.
    def exitRaiseerror_statement(self, ctx:tsqlParser.Raiseerror_statementContext):
        pass


    # Enter a parse tree produced by tsqlParser#another_statement.
    def enterAnother_statement(self, ctx:tsqlParser.Another_statementContext):
        pass

    # Exit a parse tree produced by tsqlParser#another_statement.
    def exitAnother_statement(self, ctx:tsqlParser.Another_statementContext):
        pass


    # Enter a parse tree produced by tsqlParser#delete_statement.
    def enterDelete_statement(self, ctx:tsqlParser.Delete_statementContext):
        pass

    # Exit a parse tree produced by tsqlParser#delete_statement.
    def exitDelete_statement(self, ctx:tsqlParser.Delete_statementContext):
        pass


    # Enter a parse tree produced by tsqlParser#delete_statement_from.
    def enterDelete_statement_from(self, ctx:tsqlParser.Delete_statement_fromContext):
        pass

    # Exit a parse tree produced by tsqlParser#delete_statement_from.
    def exitDelete_statement_from(self, ctx:tsqlParser.Delete_statement_fromContext):
        pass


    # Enter a parse tree produced by tsqlParser#insert_statement.
    def enterInsert_statement(self, ctx:tsqlParser.Insert_statementContext):
        pass

    # Exit a parse tree produced by tsqlParser#insert_statement.
    def exitInsert_statement(self, ctx:tsqlParser.Insert_statementContext):
        pass


    # Enter a parse tree produced by tsqlParser#insert_statement_value.
    def enterInsert_statement_value(self, ctx:tsqlParser.Insert_statement_valueContext):
        pass

    # Exit a parse tree produced by tsqlParser#insert_statement_value.
    def exitInsert_statement_value(self, ctx:tsqlParser.Insert_statement_valueContext):
        pass


    # Enter a parse tree produced by tsqlParser#select_statement.
    def enterSelect_statement(self, ctx:tsqlParser.Select_statementContext):
        pass

    # Exit a parse tree produced by tsqlParser#select_statement.
    def exitSelect_statement(self, ctx:tsqlParser.Select_statementContext):
        pass


    # Enter a parse tree produced by tsqlParser#update_statement.
    def enterUpdate_statement(self, ctx:tsqlParser.Update_statementContext):
        pass

    # Exit a parse tree produced by tsqlParser#update_statement.
    def exitUpdate_statement(self, ctx:tsqlParser.Update_statementContext):
        pass


    # Enter a parse tree produced by tsqlParser#output_clause.
    def enterOutput_clause(self, ctx:tsqlParser.Output_clauseContext):
        pass

    # Exit a parse tree produced by tsqlParser#output_clause.
    def exitOutput_clause(self, ctx:tsqlParser.Output_clauseContext):
        pass


    # Enter a parse tree produced by tsqlParser#output_dml_list_elem.
    def enterOutput_dml_list_elem(self, ctx:tsqlParser.Output_dml_list_elemContext):
        pass

    # Exit a parse tree produced by tsqlParser#output_dml_list_elem.
    def exitOutput_dml_list_elem(self, ctx:tsqlParser.Output_dml_list_elemContext):
        pass


    # Enter a parse tree produced by tsqlParser#output_column_name.
    def enterOutput_column_name(self, ctx:tsqlParser.Output_column_nameContext):
        pass

    # Exit a parse tree produced by tsqlParser#output_column_name.
    def exitOutput_column_name(self, ctx:tsqlParser.Output_column_nameContext):
        pass


    # Enter a parse tree produced by tsqlParser#create_database.
    def enterCreate_database(self, ctx:tsqlParser.Create_databaseContext):
        pass

    # Exit a parse tree produced by tsqlParser#create_database.
    def exitCreate_database(self, ctx:tsqlParser.Create_databaseContext):
        pass


    # Enter a parse tree produced by tsqlParser#create_index.
    def enterCreate_index(self, ctx:tsqlParser.Create_indexContext):
        pass

    # Exit a parse tree produced by tsqlParser#create_index.
    def exitCreate_index(self, ctx:tsqlParser.Create_indexContext):
        pass

    # Enter a parse tree produced by tsqlParser#create_trigger.
    def enterCreate_trigger(self, ctx:tsqlParser.Create_triggerContext):
        print('enter create trigger', ctx.simple_name().getText())

    # Exit a parse tree produced by tsqlParser#create_trigger.
    def exitCreate_trigger(self, ctx:tsqlParser.Create_triggerContext):
        print('exit create trigger', ctx.simple_name().getText())

    # Enter a parse tree produced by tsqlParser#create_procedure.
    def enterCreate_procedure(self, ctx:tsqlParser.Create_procedureContext):
        print('enter create procedure', ctx.func_proc_name().getText())

    # Exit a parse tree produced by tsqlParser#create_procedure.
    def exitCreate_procedure(self, ctx:tsqlParser.Create_procedureContext):
        print('exit create procedure', ctx.func_proc_name().getText())


    # Enter a parse tree produced by tsqlParser#procedure_param.
    def enterProcedure_param(self, ctx:tsqlParser.Procedure_paramContext):
        pass

    # Exit a parse tree produced by tsqlParser#procedure_param.
    def exitProcedure_param(self, ctx:tsqlParser.Procedure_paramContext):
        pass


    # Enter a parse tree produced by tsqlParser#procedure_option.
    def enterProcedure_option(self, ctx:tsqlParser.Procedure_optionContext):
        pass

    # Exit a parse tree produced by tsqlParser#procedure_option.
    def exitProcedure_option(self, ctx:tsqlParser.Procedure_optionContext):
        pass


    # Enter a parse tree produced by tsqlParser#create_statistics.
    def enterCreate_statistics(self, ctx:tsqlParser.Create_statisticsContext):
        pass

    # Exit a parse tree produced by tsqlParser#create_statistics.
    def exitCreate_statistics(self, ctx:tsqlParser.Create_statisticsContext):
        pass


    # Enter a parse tree produced by tsqlParser#create_table.
    def enterCreate_table(self, ctx:tsqlParser.Create_tableContext):
        pass

    # Exit a parse tree produced by tsqlParser#create_table.
    def exitCreate_table(self, ctx:tsqlParser.Create_tableContext):
        pass


    # Enter a parse tree produced by tsqlParser#create_view.
    def enterCreate_view(self, ctx:tsqlParser.Create_viewContext):
        pass

    # Exit a parse tree produced by tsqlParser#create_view.
    def exitCreate_view(self, ctx:tsqlParser.Create_viewContext):
        pass


    # Enter a parse tree produced by tsqlParser#view_attribute.
    def enterView_attribute(self, ctx:tsqlParser.View_attributeContext):
        pass

    # Exit a parse tree produced by tsqlParser#view_attribute.
    def exitView_attribute(self, ctx:tsqlParser.View_attributeContext):
        pass


    # Enter a parse tree produced by tsqlParser#alter_table.
    def enterAlter_table(self, ctx:tsqlParser.Alter_tableContext):
        pass

    # Exit a parse tree produced by tsqlParser#alter_table.
    def exitAlter_table(self, ctx:tsqlParser.Alter_tableContext):
        pass


    # Enter a parse tree produced by tsqlParser#alter_database.
    def enterAlter_database(self, ctx:tsqlParser.Alter_databaseContext):
        pass

    # Exit a parse tree produced by tsqlParser#alter_database.
    def exitAlter_database(self, ctx:tsqlParser.Alter_databaseContext):
        pass


    # Enter a parse tree produced by tsqlParser#database_optionspec.
    def enterDatabase_optionspec(self, ctx:tsqlParser.Database_optionspecContext):
        pass

    # Exit a parse tree produced by tsqlParser#database_optionspec.
    def exitDatabase_optionspec(self, ctx:tsqlParser.Database_optionspecContext):
        pass


    # Enter a parse tree produced by tsqlParser#auto_option.
    def enterAuto_option(self, ctx:tsqlParser.Auto_optionContext):
        pass

    # Exit a parse tree produced by tsqlParser#auto_option.
    def exitAuto_option(self, ctx:tsqlParser.Auto_optionContext):
        pass


    # Enter a parse tree produced by tsqlParser#change_tracking_option.
    def enterChange_tracking_option(self, ctx:tsqlParser.Change_tracking_optionContext):
        pass

    # Exit a parse tree produced by tsqlParser#change_tracking_option.
    def exitChange_tracking_option(self, ctx:tsqlParser.Change_tracking_optionContext):
        pass


    # Enter a parse tree produced by tsqlParser#change_tracking_option_list.
    def enterChange_tracking_option_list(self, ctx:tsqlParser.Change_tracking_option_listContext):
        pass

    # Exit a parse tree produced by tsqlParser#change_tracking_option_list.
    def exitChange_tracking_option_list(self, ctx:tsqlParser.Change_tracking_option_listContext):
        pass


    # Enter a parse tree produced by tsqlParser#containment_option.
    def enterContainment_option(self, ctx:tsqlParser.Containment_optionContext):
        pass

    # Exit a parse tree produced by tsqlParser#containment_option.
    def exitContainment_option(self, ctx:tsqlParser.Containment_optionContext):
        pass


    # Enter a parse tree produced by tsqlParser#cursor_option.
    def enterCursor_option(self, ctx:tsqlParser.Cursor_optionContext):
        pass

    # Exit a parse tree produced by tsqlParser#cursor_option.
    def exitCursor_option(self, ctx:tsqlParser.Cursor_optionContext):
        pass


    # Enter a parse tree produced by tsqlParser#date_correlation_optimization_option.
    def enterDate_correlation_optimization_option(self, ctx:tsqlParser.Date_correlation_optimization_optionContext):
        pass

    # Exit a parse tree produced by tsqlParser#date_correlation_optimization_option.
    def exitDate_correlation_optimization_option(self, ctx:tsqlParser.Date_correlation_optimization_optionContext):
        pass


    # Enter a parse tree produced by tsqlParser#db_encryption_option.
    def enterDb_encryption_option(self, ctx:tsqlParser.Db_encryption_optionContext):
        pass

    # Exit a parse tree produced by tsqlParser#db_encryption_option.
    def exitDb_encryption_option(self, ctx:tsqlParser.Db_encryption_optionContext):
        pass


    # Enter a parse tree produced by tsqlParser#db_state_option.
    def enterDb_state_option(self, ctx:tsqlParser.Db_state_optionContext):
        pass

    # Exit a parse tree produced by tsqlParser#db_state_option.
    def exitDb_state_option(self, ctx:tsqlParser.Db_state_optionContext):
        pass


    # Enter a parse tree produced by tsqlParser#db_update_option.
    def enterDb_update_option(self, ctx:tsqlParser.Db_update_optionContext):
        pass

    # Exit a parse tree produced by tsqlParser#db_update_option.
    def exitDb_update_option(self, ctx:tsqlParser.Db_update_optionContext):
        pass


    # Enter a parse tree produced by tsqlParser#db_user_access_option.
    def enterDb_user_access_option(self, ctx:tsqlParser.Db_user_access_optionContext):
        pass

    # Exit a parse tree produced by tsqlParser#db_user_access_option.
    def exitDb_user_access_option(self, ctx:tsqlParser.Db_user_access_optionContext):
        pass


    # Enter a parse tree produced by tsqlParser#delayed_durability_option.
    def enterDelayed_durability_option(self, ctx:tsqlParser.Delayed_durability_optionContext):
        pass

    # Exit a parse tree produced by tsqlParser#delayed_durability_option.
    def exitDelayed_durability_option(self, ctx:tsqlParser.Delayed_durability_optionContext):
        pass


    # Enter a parse tree produced by tsqlParser#external_access_option.
    def enterExternal_access_option(self, ctx:tsqlParser.External_access_optionContext):
        pass

    # Exit a parse tree produced by tsqlParser#external_access_option.
    def exitExternal_access_option(self, ctx:tsqlParser.External_access_optionContext):
        pass


    # Enter a parse tree produced by tsqlParser#mixed_page_allocation_option.
    def enterMixed_page_allocation_option(self, ctx:tsqlParser.Mixed_page_allocation_optionContext):
        pass

    # Exit a parse tree produced by tsqlParser#mixed_page_allocation_option.
    def exitMixed_page_allocation_option(self, ctx:tsqlParser.Mixed_page_allocation_optionContext):
        pass


    # Enter a parse tree produced by tsqlParser#parameterization_option.
    def enterParameterization_option(self, ctx:tsqlParser.Parameterization_optionContext):
        pass

    # Exit a parse tree produced by tsqlParser#parameterization_option.
    def exitParameterization_option(self, ctx:tsqlParser.Parameterization_optionContext):
        pass


    # Enter a parse tree produced by tsqlParser#recovery_option.
    def enterRecovery_option(self, ctx:tsqlParser.Recovery_optionContext):
        pass

    # Exit a parse tree produced by tsqlParser#recovery_option.
    def exitRecovery_option(self, ctx:tsqlParser.Recovery_optionContext):
        pass


    # Enter a parse tree produced by tsqlParser#service_broker_option.
    def enterService_broker_option(self, ctx:tsqlParser.Service_broker_optionContext):
        pass

    # Exit a parse tree produced by tsqlParser#service_broker_option.
    def exitService_broker_option(self, ctx:tsqlParser.Service_broker_optionContext):
        pass


    # Enter a parse tree produced by tsqlParser#snapshot_option.
    def enterSnapshot_option(self, ctx:tsqlParser.Snapshot_optionContext):
        pass

    # Exit a parse tree produced by tsqlParser#snapshot_option.
    def exitSnapshot_option(self, ctx:tsqlParser.Snapshot_optionContext):
        pass


    # Enter a parse tree produced by tsqlParser#sql_option.
    def enterSql_option(self, ctx:tsqlParser.Sql_optionContext):
        pass

    # Exit a parse tree produced by tsqlParser#sql_option.
    def exitSql_option(self, ctx:tsqlParser.Sql_optionContext):
        pass


    # Enter a parse tree produced by tsqlParser#target_recovery_time_option.
    def enterTarget_recovery_time_option(self, ctx:tsqlParser.Target_recovery_time_optionContext):
        pass

    # Exit a parse tree produced by tsqlParser#target_recovery_time_option.
    def exitTarget_recovery_time_option(self, ctx:tsqlParser.Target_recovery_time_optionContext):
        pass


    # Enter a parse tree produced by tsqlParser#termination.
    def enterTermination(self, ctx:tsqlParser.TerminationContext):
        pass

    # Exit a parse tree produced by tsqlParser#termination.
    def exitTermination(self, ctx:tsqlParser.TerminationContext):
        pass


    # Enter a parse tree produced by tsqlParser#drop_index.
    def enterDrop_index(self, ctx:tsqlParser.Drop_indexContext):
        pass

    # Exit a parse tree produced by tsqlParser#drop_index.
    def exitDrop_index(self, ctx:tsqlParser.Drop_indexContext):
        pass


    # Enter a parse tree produced by tsqlParser#drop_procedure.
    def enterDrop_procedure(self, ctx:tsqlParser.Drop_procedureContext):
        pass

    # Exit a parse tree produced by tsqlParser#drop_procedure.
    def exitDrop_procedure(self, ctx:tsqlParser.Drop_procedureContext):
        pass


    # Enter a parse tree produced by tsqlParser#drop_statistics.
    def enterDrop_statistics(self, ctx:tsqlParser.Drop_statisticsContext):
        pass

    # Exit a parse tree produced by tsqlParser#drop_statistics.
    def exitDrop_statistics(self, ctx:tsqlParser.Drop_statisticsContext):
        pass


    # Enter a parse tree produced by tsqlParser#drop_table.
    def enterDrop_table(self, ctx:tsqlParser.Drop_tableContext):
        pass

    # Exit a parse tree produced by tsqlParser#drop_table.
    def exitDrop_table(self, ctx:tsqlParser.Drop_tableContext):
        pass


    # Enter a parse tree produced by tsqlParser#drop_view.
    def enterDrop_view(self, ctx:tsqlParser.Drop_viewContext):
        pass

    # Exit a parse tree produced by tsqlParser#drop_view.
    def exitDrop_view(self, ctx:tsqlParser.Drop_viewContext):
        pass


    # Enter a parse tree produced by tsqlParser#create_type.
    def enterCreate_type(self, ctx:tsqlParser.Create_typeContext):
        pass

    # Exit a parse tree produced by tsqlParser#create_type.
    def exitCreate_type(self, ctx:tsqlParser.Create_typeContext):
        pass


    # Enter a parse tree produced by tsqlParser#drop_type.
    def enterDrop_type(self, ctx:tsqlParser.Drop_typeContext):
        pass

    # Exit a parse tree produced by tsqlParser#drop_type.
    def exitDrop_type(self, ctx:tsqlParser.Drop_typeContext):
        pass


    # Enter a parse tree produced by tsqlParser#rowset_function_limited.
    def enterRowset_function_limited(self, ctx:tsqlParser.Rowset_function_limitedContext):
        pass

    # Exit a parse tree produced by tsqlParser#rowset_function_limited.
    def exitRowset_function_limited(self, ctx:tsqlParser.Rowset_function_limitedContext):
        pass


    # Enter a parse tree produced by tsqlParser#openquery.
    def enterOpenquery(self, ctx:tsqlParser.OpenqueryContext):
        pass

    # Exit a parse tree produced by tsqlParser#openquery.
    def exitOpenquery(self, ctx:tsqlParser.OpenqueryContext):
        pass


    # Enter a parse tree produced by tsqlParser#opendatasource.
    def enterOpendatasource(self, ctx:tsqlParser.OpendatasourceContext):
        pass

    # Exit a parse tree produced by tsqlParser#opendatasource.
    def exitOpendatasource(self, ctx:tsqlParser.OpendatasourceContext):
        pass


    # Enter a parse tree produced by tsqlParser#declare_statement.
    def enterDeclare_statement(self, ctx:tsqlParser.Declare_statementContext):
        pass

    # Exit a parse tree produced by tsqlParser#declare_statement.
    def exitDeclare_statement(self, ctx:tsqlParser.Declare_statementContext):
        pass


    # Enter a parse tree produced by tsqlParser#cursor_statement.
    def enterCursor_statement(self, ctx:tsqlParser.Cursor_statementContext):
        pass

    # Exit a parse tree produced by tsqlParser#cursor_statement.
    def exitCursor_statement(self, ctx:tsqlParser.Cursor_statementContext):
        pass


    # Enter a parse tree produced by tsqlParser#execute_statement.
    def enterExecute_statement(self, ctx:tsqlParser.Execute_statementContext):
        pass

    # Exit a parse tree produced by tsqlParser#execute_statement.
    def exitExecute_statement(self, ctx:tsqlParser.Execute_statementContext):
        pass


    # Enter a parse tree produced by tsqlParser#execute_statement_arg.
    def enterExecute_statement_arg(self, ctx:tsqlParser.Execute_statement_argContext):
        pass

    # Exit a parse tree produced by tsqlParser#execute_statement_arg.
    def exitExecute_statement_arg(self, ctx:tsqlParser.Execute_statement_argContext):
        pass


    # Enter a parse tree produced by tsqlParser#execute_var_string.
    def enterExecute_var_string(self, ctx:tsqlParser.Execute_var_stringContext):
        pass

    # Exit a parse tree produced by tsqlParser#execute_var_string.
    def exitExecute_var_string(self, ctx:tsqlParser.Execute_var_stringContext):
        pass


    # Enter a parse tree produced by tsqlParser#security_statement.
    def enterSecurity_statement(self, ctx:tsqlParser.Security_statementContext):
        pass

    # Exit a parse tree produced by tsqlParser#security_statement.
    def exitSecurity_statement(self, ctx:tsqlParser.Security_statementContext):
        pass


    # Enter a parse tree produced by tsqlParser#grant_permission.
    def enterGrant_permission(self, ctx:tsqlParser.Grant_permissionContext):
        pass

    # Exit a parse tree produced by tsqlParser#grant_permission.
    def exitGrant_permission(self, ctx:tsqlParser.Grant_permissionContext):
        pass


    # Enter a parse tree produced by tsqlParser#set_statement.
    def enterSet_statement(self, ctx:tsqlParser.Set_statementContext):
        pass

    # Exit a parse tree produced by tsqlParser#set_statement.
    def exitSet_statement(self, ctx:tsqlParser.Set_statementContext):
        pass


    # Enter a parse tree produced by tsqlParser#transaction_statement.
    def enterTransaction_statement(self, ctx:tsqlParser.Transaction_statementContext):
        pass

    # Exit a parse tree produced by tsqlParser#transaction_statement.
    def exitTransaction_statement(self, ctx:tsqlParser.Transaction_statementContext):
        pass


    # Enter a parse tree produced by tsqlParser#go_statement.
    def enterGo_statement(self, ctx:tsqlParser.Go_statementContext):
        print('enter GO')

    # Exit a parse tree produced by tsqlParser#go_statement.
    def exitGo_statement(self, ctx:tsqlParser.Go_statementContext):
        print('exit GO')


    # Enter a parse tree produced by tsqlParser#use_statement.
    def enterUse_statement(self, ctx:tsqlParser.Use_statementContext):
        pass

    # Exit a parse tree produced by tsqlParser#use_statement.
    def exitUse_statement(self, ctx:tsqlParser.Use_statementContext):
        pass


    # Enter a parse tree produced by tsqlParser#execute_clause.
    def enterExecute_clause(self, ctx:tsqlParser.Execute_clauseContext):
        pass

    # Exit a parse tree produced by tsqlParser#execute_clause.
    def exitExecute_clause(self, ctx:tsqlParser.Execute_clauseContext):
        pass


    # Enter a parse tree produced by tsqlParser#declare_local.
    def enterDeclare_local(self, ctx:tsqlParser.Declare_localContext):
        pass

    # Exit a parse tree produced by tsqlParser#declare_local.
    def exitDeclare_local(self, ctx:tsqlParser.Declare_localContext):
        pass


    # Enter a parse tree produced by tsqlParser#table_type_definition.
    def enterTable_type_definition(self, ctx:tsqlParser.Table_type_definitionContext):
        pass

    # Exit a parse tree produced by tsqlParser#table_type_definition.
    def exitTable_type_definition(self, ctx:tsqlParser.Table_type_definitionContext):
        pass


    # Enter a parse tree produced by tsqlParser#column_def_table_constraints.
    def enterColumn_def_table_constraints(self, ctx:tsqlParser.Column_def_table_constraintsContext):
        pass

    # Exit a parse tree produced by tsqlParser#column_def_table_constraints.
    def exitColumn_def_table_constraints(self, ctx:tsqlParser.Column_def_table_constraintsContext):
        pass


    # Enter a parse tree produced by tsqlParser#column_def_table_constraint.
    def enterColumn_def_table_constraint(self, ctx:tsqlParser.Column_def_table_constraintContext):
        pass

    # Exit a parse tree produced by tsqlParser#column_def_table_constraint.
    def exitColumn_def_table_constraint(self, ctx:tsqlParser.Column_def_table_constraintContext):
        pass


    # Enter a parse tree produced by tsqlParser#column_definition.
    def enterColumn_definition(self, ctx:tsqlParser.Column_definitionContext):
        pass

    # Exit a parse tree produced by tsqlParser#column_definition.
    def exitColumn_definition(self, ctx:tsqlParser.Column_definitionContext):
        pass


    # Enter a parse tree produced by tsqlParser#column_constraint.
    def enterColumn_constraint(self, ctx:tsqlParser.Column_constraintContext):
        pass

    # Exit a parse tree produced by tsqlParser#column_constraint.
    def exitColumn_constraint(self, ctx:tsqlParser.Column_constraintContext):
        pass


    # Enter a parse tree produced by tsqlParser#table_constraint.
    def enterTable_constraint(self, ctx:tsqlParser.Table_constraintContext):
        pass

    # Exit a parse tree produced by tsqlParser#table_constraint.
    def exitTable_constraint(self, ctx:tsqlParser.Table_constraintContext):
        pass


    # Enter a parse tree produced by tsqlParser#index_options.
    def enterIndex_options(self, ctx:tsqlParser.Index_optionsContext):
        pass

    # Exit a parse tree produced by tsqlParser#index_options.
    def exitIndex_options(self, ctx:tsqlParser.Index_optionsContext):
        pass


    # Enter a parse tree produced by tsqlParser#index_option.
    def enterIndex_option(self, ctx:tsqlParser.Index_optionContext):
        pass

    # Exit a parse tree produced by tsqlParser#index_option.
    def exitIndex_option(self, ctx:tsqlParser.Index_optionContext):
        pass


    # Enter a parse tree produced by tsqlParser#declare_cursor.
    def enterDeclare_cursor(self, ctx:tsqlParser.Declare_cursorContext):
        pass

    # Exit a parse tree produced by tsqlParser#declare_cursor.
    def exitDeclare_cursor(self, ctx:tsqlParser.Declare_cursorContext):
        pass


    # Enter a parse tree produced by tsqlParser#declare_set_cursor_common.
    def enterDeclare_set_cursor_common(self, ctx:tsqlParser.Declare_set_cursor_commonContext):
        pass

    # Exit a parse tree produced by tsqlParser#declare_set_cursor_common.
    def exitDeclare_set_cursor_common(self, ctx:tsqlParser.Declare_set_cursor_commonContext):
        pass


    # Enter a parse tree produced by tsqlParser#fetch_cursor.
    def enterFetch_cursor(self, ctx:tsqlParser.Fetch_cursorContext):
        pass

    # Exit a parse tree produced by tsqlParser#fetch_cursor.
    def exitFetch_cursor(self, ctx:tsqlParser.Fetch_cursorContext):
        pass


    # Enter a parse tree produced by tsqlParser#set_special.
    def enterSet_special(self, ctx:tsqlParser.Set_specialContext):
        pass

    # Exit a parse tree produced by tsqlParser#set_special.
    def exitSet_special(self, ctx:tsqlParser.Set_specialContext):
        pass


    # Enter a parse tree produced by tsqlParser#constant_LOCAL_ID.
    def enterConstant_LOCAL_ID(self, ctx:tsqlParser.Constant_LOCAL_IDContext):
        pass

    # Exit a parse tree produced by tsqlParser#constant_LOCAL_ID.
    def exitConstant_LOCAL_ID(self, ctx:tsqlParser.Constant_LOCAL_IDContext):
        pass


    # Enter a parse tree produced by tsqlParser#binary_operator_expression.
    def enterBinary_operator_expression(self, ctx:tsqlParser.Binary_operator_expressionContext):
        pass

    # Exit a parse tree produced by tsqlParser#binary_operator_expression.
    def exitBinary_operator_expression(self, ctx:tsqlParser.Binary_operator_expressionContext):
        pass


    # Enter a parse tree produced by tsqlParser#primitive_expression.
    def enterPrimitive_expression(self, ctx:tsqlParser.Primitive_expressionContext):
        pass

    # Exit a parse tree produced by tsqlParser#primitive_expression.
    def exitPrimitive_expression(self, ctx:tsqlParser.Primitive_expressionContext):
        pass


    # Enter a parse tree produced by tsqlParser#unary_operator_expression.
    def enterUnary_operator_expression(self, ctx:tsqlParser.Unary_operator_expressionContext):
        pass

    # Exit a parse tree produced by tsqlParser#unary_operator_expression.
    def exitUnary_operator_expression(self, ctx:tsqlParser.Unary_operator_expressionContext):
        pass


    # Enter a parse tree produced by tsqlParser#bracket_expression.
    def enterBracket_expression(self, ctx:tsqlParser.Bracket_expressionContext):
        pass

    # Exit a parse tree produced by tsqlParser#bracket_expression.
    def exitBracket_expression(self, ctx:tsqlParser.Bracket_expressionContext):
        pass


    # Enter a parse tree produced by tsqlParser#function_call_expression.
    def enterFunction_call_expression(self, ctx:tsqlParser.Function_call_expressionContext):
        pass

    # Exit a parse tree produced by tsqlParser#function_call_expression.
    def exitFunction_call_expression(self, ctx:tsqlParser.Function_call_expressionContext):
        pass


    # Enter a parse tree produced by tsqlParser#case_expression.
    def enterCase_expression(self, ctx:tsqlParser.Case_expressionContext):
        pass

    # Exit a parse tree produced by tsqlParser#case_expression.
    def exitCase_expression(self, ctx:tsqlParser.Case_expressionContext):
        pass


    # Enter a parse tree produced by tsqlParser#column_ref_expression.
    def enterColumn_ref_expression(self, ctx:tsqlParser.Column_ref_expressionContext):
        pass

    # Exit a parse tree produced by tsqlParser#column_ref_expression.
    def exitColumn_ref_expression(self, ctx:tsqlParser.Column_ref_expressionContext):
        pass


    # Enter a parse tree produced by tsqlParser#subquery_expression.
    def enterSubquery_expression(self, ctx:tsqlParser.Subquery_expressionContext):
        pass

    # Exit a parse tree produced by tsqlParser#subquery_expression.
    def exitSubquery_expression(self, ctx:tsqlParser.Subquery_expressionContext):
        pass


    # Enter a parse tree produced by tsqlParser#over_clause_expression.
    def enterOver_clause_expression(self, ctx:tsqlParser.Over_clause_expressionContext):
        pass

    # Exit a parse tree produced by tsqlParser#over_clause_expression.
    def exitOver_clause_expression(self, ctx:tsqlParser.Over_clause_expressionContext):
        pass


    # Enter a parse tree produced by tsqlParser#constant_expression.
    def enterConstant_expression(self, ctx:tsqlParser.Constant_expressionContext):
        pass

    # Exit a parse tree produced by tsqlParser#constant_expression.
    def exitConstant_expression(self, ctx:tsqlParser.Constant_expressionContext):
        pass


    # Enter a parse tree produced by tsqlParser#subquery.
    def enterSubquery(self, ctx:tsqlParser.SubqueryContext):
        pass

    # Exit a parse tree produced by tsqlParser#subquery.
    def exitSubquery(self, ctx:tsqlParser.SubqueryContext):
        pass


    # Enter a parse tree produced by tsqlParser#with_expression.
    def enterWith_expression(self, ctx:tsqlParser.With_expressionContext):
        pass

    # Exit a parse tree produced by tsqlParser#with_expression.
    def exitWith_expression(self, ctx:tsqlParser.With_expressionContext):
        pass


    # Enter a parse tree produced by tsqlParser#common_table_expression.
    def enterCommon_table_expression(self, ctx:tsqlParser.Common_table_expressionContext):
        pass

    # Exit a parse tree produced by tsqlParser#common_table_expression.
    def exitCommon_table_expression(self, ctx:tsqlParser.Common_table_expressionContext):
        pass


    # Enter a parse tree produced by tsqlParser#update_elem.
    def enterUpdate_elem(self, ctx:tsqlParser.Update_elemContext):
        pass

    # Exit a parse tree produced by tsqlParser#update_elem.
    def exitUpdate_elem(self, ctx:tsqlParser.Update_elemContext):
        pass


    # Enter a parse tree produced by tsqlParser#search_condition_list.
    def enterSearch_condition_list(self, ctx:tsqlParser.Search_condition_listContext):
        pass

    # Exit a parse tree produced by tsqlParser#search_condition_list.
    def exitSearch_condition_list(self, ctx:tsqlParser.Search_condition_listContext):
        pass


    # Enter a parse tree produced by tsqlParser#search_condition.
    def enterSearch_condition(self, ctx:tsqlParser.Search_conditionContext):
        pass

    # Exit a parse tree produced by tsqlParser#search_condition.
    def exitSearch_condition(self, ctx:tsqlParser.Search_conditionContext):
        pass


    # Enter a parse tree produced by tsqlParser#search_condition_and.
    def enterSearch_condition_and(self, ctx:tsqlParser.Search_condition_andContext):
        pass

    # Exit a parse tree produced by tsqlParser#search_condition_and.
    def exitSearch_condition_and(self, ctx:tsqlParser.Search_condition_andContext):
        pass


    # Enter a parse tree produced by tsqlParser#search_condition_not.
    def enterSearch_condition_not(self, ctx:tsqlParser.Search_condition_notContext):
        pass

    # Exit a parse tree produced by tsqlParser#search_condition_not.
    def exitSearch_condition_not(self, ctx:tsqlParser.Search_condition_notContext):
        pass


    # Enter a parse tree produced by tsqlParser#predicate.
    def enterPredicate(self, ctx:tsqlParser.PredicateContext):
        pass

    # Exit a parse tree produced by tsqlParser#predicate.
    def exitPredicate(self, ctx:tsqlParser.PredicateContext):
        pass


    # Enter a parse tree produced by tsqlParser#query_expression.
    def enterQuery_expression(self, ctx:tsqlParser.Query_expressionContext):
        pass

    # Exit a parse tree produced by tsqlParser#query_expression.
    def exitQuery_expression(self, ctx:tsqlParser.Query_expressionContext):
        pass


    # Enter a parse tree produced by tsqlParser#union.
    def enterUnion(self, ctx:tsqlParser.UnionContext):
        pass

    # Exit a parse tree produced by tsqlParser#union.
    def exitUnion(self, ctx:tsqlParser.UnionContext):
        pass


    # Enter a parse tree produced by tsqlParser#query_specification.
    def enterQuery_specification(self, ctx:tsqlParser.Query_specificationContext):
        pass

    # Exit a parse tree produced by tsqlParser#query_specification.
    def exitQuery_specification(self, ctx:tsqlParser.Query_specificationContext):
        pass


    # Enter a parse tree produced by tsqlParser#order_by_clause.
    def enterOrder_by_clause(self, ctx:tsqlParser.Order_by_clauseContext):
        pass

    # Exit a parse tree produced by tsqlParser#order_by_clause.
    def exitOrder_by_clause(self, ctx:tsqlParser.Order_by_clauseContext):
        pass


    # Enter a parse tree produced by tsqlParser#for_clause.
    def enterFor_clause(self, ctx:tsqlParser.For_clauseContext):
        pass

    # Exit a parse tree produced by tsqlParser#for_clause.
    def exitFor_clause(self, ctx:tsqlParser.For_clauseContext):
        pass


    # Enter a parse tree produced by tsqlParser#xml_common_directives.
    def enterXml_common_directives(self, ctx:tsqlParser.Xml_common_directivesContext):
        pass

    # Exit a parse tree produced by tsqlParser#xml_common_directives.
    def exitXml_common_directives(self, ctx:tsqlParser.Xml_common_directivesContext):
        pass


    # Enter a parse tree produced by tsqlParser#order_by_expression.
    def enterOrder_by_expression(self, ctx:tsqlParser.Order_by_expressionContext):
        pass

    # Exit a parse tree produced by tsqlParser#order_by_expression.
    def exitOrder_by_expression(self, ctx:tsqlParser.Order_by_expressionContext):
        pass


    # Enter a parse tree produced by tsqlParser#group_by_item.
    def enterGroup_by_item(self, ctx:tsqlParser.Group_by_itemContext):
        pass

    # Exit a parse tree produced by tsqlParser#group_by_item.
    def exitGroup_by_item(self, ctx:tsqlParser.Group_by_itemContext):
        pass


    # Enter a parse tree produced by tsqlParser#option_clause.
    def enterOption_clause(self, ctx:tsqlParser.Option_clauseContext):
        pass

    # Exit a parse tree produced by tsqlParser#option_clause.
    def exitOption_clause(self, ctx:tsqlParser.Option_clauseContext):
        pass


    # Enter a parse tree produced by tsqlParser#option.
    def enterOption(self, ctx:tsqlParser.OptionContext):
        pass

    # Exit a parse tree produced by tsqlParser#option.
    def exitOption(self, ctx:tsqlParser.OptionContext):
        pass


    # Enter a parse tree produced by tsqlParser#optimize_for_arg.
    def enterOptimize_for_arg(self, ctx:tsqlParser.Optimize_for_argContext):
        pass

    # Exit a parse tree produced by tsqlParser#optimize_for_arg.
    def exitOptimize_for_arg(self, ctx:tsqlParser.Optimize_for_argContext):
        pass


    # Enter a parse tree produced by tsqlParser#select_list.
    def enterSelect_list(self, ctx:tsqlParser.Select_listContext):
        pass

    # Exit a parse tree produced by tsqlParser#select_list.
    def exitSelect_list(self, ctx:tsqlParser.Select_listContext):
        pass


    # Enter a parse tree produced by tsqlParser#select_list_elem.
    def enterSelect_list_elem(self, ctx:tsqlParser.Select_list_elemContext):
        pass

    # Exit a parse tree produced by tsqlParser#select_list_elem.
    def exitSelect_list_elem(self, ctx:tsqlParser.Select_list_elemContext):
        pass


    # Enter a parse tree produced by tsqlParser#table_sources.
    def enterTable_sources(self, ctx:tsqlParser.Table_sourcesContext):
        pass

    # Exit a parse tree produced by tsqlParser#table_sources.
    def exitTable_sources(self, ctx:tsqlParser.Table_sourcesContext):
        pass


    # Enter a parse tree produced by tsqlParser#table_source.
    def enterTable_source(self, ctx:tsqlParser.Table_sourceContext):
        pass

    # Exit a parse tree produced by tsqlParser#table_source.
    def exitTable_source(self, ctx:tsqlParser.Table_sourceContext):
        pass


    # Enter a parse tree produced by tsqlParser#table_source_item_joined.
    def enterTable_source_item_joined(self, ctx:tsqlParser.Table_source_item_joinedContext):
        pass

    # Exit a parse tree produced by tsqlParser#table_source_item_joined.
    def exitTable_source_item_joined(self, ctx:tsqlParser.Table_source_item_joinedContext):
        pass


    # Enter a parse tree produced by tsqlParser#table_source_item.
    def enterTable_source_item(self, ctx:tsqlParser.Table_source_itemContext):
        pass

    # Exit a parse tree produced by tsqlParser#table_source_item.
    def exitTable_source_item(self, ctx:tsqlParser.Table_source_itemContext):
        pass


    # Enter a parse tree produced by tsqlParser#change_table.
    def enterChange_table(self, ctx:tsqlParser.Change_tableContext):
        pass

    # Exit a parse tree produced by tsqlParser#change_table.
    def exitChange_table(self, ctx:tsqlParser.Change_tableContext):
        pass


    # Enter a parse tree produced by tsqlParser#join_part.
    def enterJoin_part(self, ctx:tsqlParser.Join_partContext):
        pass

    # Exit a parse tree produced by tsqlParser#join_part.
    def exitJoin_part(self, ctx:tsqlParser.Join_partContext):
        pass


    # Enter a parse tree produced by tsqlParser#table_name_with_hint.
    def enterTable_name_with_hint(self, ctx:tsqlParser.Table_name_with_hintContext):
        pass

    # Exit a parse tree produced by tsqlParser#table_name_with_hint.
    def exitTable_name_with_hint(self, ctx:tsqlParser.Table_name_with_hintContext):
        pass


    # Enter a parse tree produced by tsqlParser#rowset_function.
    def enterRowset_function(self, ctx:tsqlParser.Rowset_functionContext):
        pass

    # Exit a parse tree produced by tsqlParser#rowset_function.
    def exitRowset_function(self, ctx:tsqlParser.Rowset_functionContext):
        pass


    # Enter a parse tree produced by tsqlParser#bulk_option.
    def enterBulk_option(self, ctx:tsqlParser.Bulk_optionContext):
        pass

    # Exit a parse tree produced by tsqlParser#bulk_option.
    def exitBulk_option(self, ctx:tsqlParser.Bulk_optionContext):
        pass


    # Enter a parse tree produced by tsqlParser#derived_table.
    def enterDerived_table(self, ctx:tsqlParser.Derived_tableContext):
        pass

    # Exit a parse tree produced by tsqlParser#derived_table.
    def exitDerived_table(self, ctx:tsqlParser.Derived_tableContext):
        pass


    # Enter a parse tree produced by tsqlParser#function_call.
    def enterFunction_call(self, ctx:tsqlParser.Function_callContext):
        pass

    # Exit a parse tree produced by tsqlParser#function_call.
    def exitFunction_call(self, ctx:tsqlParser.Function_callContext):
        pass


    # Enter a parse tree produced by tsqlParser#switch_section.
    def enterSwitch_section(self, ctx:tsqlParser.Switch_sectionContext):
        pass

    # Exit a parse tree produced by tsqlParser#switch_section.
    def exitSwitch_section(self, ctx:tsqlParser.Switch_sectionContext):
        pass


    # Enter a parse tree produced by tsqlParser#switch_search_condition_section.
    def enterSwitch_search_condition_section(self, ctx:tsqlParser.Switch_search_condition_sectionContext):
        pass

    # Exit a parse tree produced by tsqlParser#switch_search_condition_section.
    def exitSwitch_search_condition_section(self, ctx:tsqlParser.Switch_search_condition_sectionContext):
        pass


    # Enter a parse tree produced by tsqlParser#as_table_alias.
    def enterAs_table_alias(self, ctx:tsqlParser.As_table_aliasContext):
        pass

    # Exit a parse tree produced by tsqlParser#as_table_alias.
    def exitAs_table_alias(self, ctx:tsqlParser.As_table_aliasContext):
        pass


    # Enter a parse tree produced by tsqlParser#table_alias.
    def enterTable_alias(self, ctx:tsqlParser.Table_aliasContext):
        pass

    # Exit a parse tree produced by tsqlParser#table_alias.
    def exitTable_alias(self, ctx:tsqlParser.Table_aliasContext):
        pass


    # Enter a parse tree produced by tsqlParser#with_table_hints.
    def enterWith_table_hints(self, ctx:tsqlParser.With_table_hintsContext):
        pass

    # Exit a parse tree produced by tsqlParser#with_table_hints.
    def exitWith_table_hints(self, ctx:tsqlParser.With_table_hintsContext):
        pass


    # Enter a parse tree produced by tsqlParser#insert_with_table_hints.
    def enterInsert_with_table_hints(self, ctx:tsqlParser.Insert_with_table_hintsContext):
        pass

    # Exit a parse tree produced by tsqlParser#insert_with_table_hints.
    def exitInsert_with_table_hints(self, ctx:tsqlParser.Insert_with_table_hintsContext):
        pass


    # Enter a parse tree produced by tsqlParser#table_hint.
    def enterTable_hint(self, ctx:tsqlParser.Table_hintContext):
        pass

    # Exit a parse tree produced by tsqlParser#table_hint.
    def exitTable_hint(self, ctx:tsqlParser.Table_hintContext):
        pass


    # Enter a parse tree produced by tsqlParser#index_value.
    def enterIndex_value(self, ctx:tsqlParser.Index_valueContext):
        pass

    # Exit a parse tree produced by tsqlParser#index_value.
    def exitIndex_value(self, ctx:tsqlParser.Index_valueContext):
        pass


    # Enter a parse tree produced by tsqlParser#column_alias_list.
    def enterColumn_alias_list(self, ctx:tsqlParser.Column_alias_listContext):
        pass

    # Exit a parse tree produced by tsqlParser#column_alias_list.
    def exitColumn_alias_list(self, ctx:tsqlParser.Column_alias_listContext):
        pass


    # Enter a parse tree produced by tsqlParser#column_alias.
    def enterColumn_alias(self, ctx:tsqlParser.Column_aliasContext):
        pass

    # Exit a parse tree produced by tsqlParser#column_alias.
    def exitColumn_alias(self, ctx:tsqlParser.Column_aliasContext):
        pass


    # Enter a parse tree produced by tsqlParser#table_value_constructor.
    def enterTable_value_constructor(self, ctx:tsqlParser.Table_value_constructorContext):
        pass

    # Exit a parse tree produced by tsqlParser#table_value_constructor.
    def exitTable_value_constructor(self, ctx:tsqlParser.Table_value_constructorContext):
        pass


    # Enter a parse tree produced by tsqlParser#expression_list.
    def enterExpression_list(self, ctx:tsqlParser.Expression_listContext):
        pass

    # Exit a parse tree produced by tsqlParser#expression_list.
    def exitExpression_list(self, ctx:tsqlParser.Expression_listContext):
        pass


    # Enter a parse tree produced by tsqlParser#ranking_windowed_function.
    def enterRanking_windowed_function(self, ctx:tsqlParser.Ranking_windowed_functionContext):
        pass

    # Exit a parse tree produced by tsqlParser#ranking_windowed_function.
    def exitRanking_windowed_function(self, ctx:tsqlParser.Ranking_windowed_functionContext):
        pass


    # Enter a parse tree produced by tsqlParser#aggregate_windowed_function.
    def enterAggregate_windowed_function(self, ctx:tsqlParser.Aggregate_windowed_functionContext):
        pass

    # Exit a parse tree produced by tsqlParser#aggregate_windowed_function.
    def exitAggregate_windowed_function(self, ctx:tsqlParser.Aggregate_windowed_functionContext):
        pass


    # Enter a parse tree produced by tsqlParser#all_distinct_expression.
    def enterAll_distinct_expression(self, ctx:tsqlParser.All_distinct_expressionContext):
        pass

    # Exit a parse tree produced by tsqlParser#all_distinct_expression.
    def exitAll_distinct_expression(self, ctx:tsqlParser.All_distinct_expressionContext):
        pass


    # Enter a parse tree produced by tsqlParser#over_clause.
    def enterOver_clause(self, ctx:tsqlParser.Over_clauseContext):
        pass

    # Exit a parse tree produced by tsqlParser#over_clause.
    def exitOver_clause(self, ctx:tsqlParser.Over_clauseContext):
        pass


    # Enter a parse tree produced by tsqlParser#row_or_range_clause.
    def enterRow_or_range_clause(self, ctx:tsqlParser.Row_or_range_clauseContext):
        pass

    # Exit a parse tree produced by tsqlParser#row_or_range_clause.
    def exitRow_or_range_clause(self, ctx:tsqlParser.Row_or_range_clauseContext):
        pass


    # Enter a parse tree produced by tsqlParser#window_frame_extent.
    def enterWindow_frame_extent(self, ctx:tsqlParser.Window_frame_extentContext):
        pass

    # Exit a parse tree produced by tsqlParser#window_frame_extent.
    def exitWindow_frame_extent(self, ctx:tsqlParser.Window_frame_extentContext):
        pass


    # Enter a parse tree produced by tsqlParser#window_frame_bound.
    def enterWindow_frame_bound(self, ctx:tsqlParser.Window_frame_boundContext):
        pass

    # Exit a parse tree produced by tsqlParser#window_frame_bound.
    def exitWindow_frame_bound(self, ctx:tsqlParser.Window_frame_boundContext):
        pass


    # Enter a parse tree produced by tsqlParser#window_frame_preceding.
    def enterWindow_frame_preceding(self, ctx:tsqlParser.Window_frame_precedingContext):
        pass

    # Exit a parse tree produced by tsqlParser#window_frame_preceding.
    def exitWindow_frame_preceding(self, ctx:tsqlParser.Window_frame_precedingContext):
        pass


    # Enter a parse tree produced by tsqlParser#window_frame_following.
    def enterWindow_frame_following(self, ctx:tsqlParser.Window_frame_followingContext):
        pass

    # Exit a parse tree produced by tsqlParser#window_frame_following.
    def exitWindow_frame_following(self, ctx:tsqlParser.Window_frame_followingContext):
        pass


    # Enter a parse tree produced by tsqlParser#create_database_option.
    def enterCreate_database_option(self, ctx:tsqlParser.Create_database_optionContext):
        pass

    # Exit a parse tree produced by tsqlParser#create_database_option.
    def exitCreate_database_option(self, ctx:tsqlParser.Create_database_optionContext):
        pass


    # Enter a parse tree produced by tsqlParser#database_filestream_option.
    def enterDatabase_filestream_option(self, ctx:tsqlParser.Database_filestream_optionContext):
        pass

    # Exit a parse tree produced by tsqlParser#database_filestream_option.
    def exitDatabase_filestream_option(self, ctx:tsqlParser.Database_filestream_optionContext):
        pass


    # Enter a parse tree produced by tsqlParser#database_file_spec.
    def enterDatabase_file_spec(self, ctx:tsqlParser.Database_file_specContext):
        pass

    # Exit a parse tree produced by tsqlParser#database_file_spec.
    def exitDatabase_file_spec(self, ctx:tsqlParser.Database_file_specContext):
        pass


    # Enter a parse tree produced by tsqlParser#file_group.
    def enterFile_group(self, ctx:tsqlParser.File_groupContext):
        pass

    # Exit a parse tree produced by tsqlParser#file_group.
    def exitFile_group(self, ctx:tsqlParser.File_groupContext):
        pass


    # Enter a parse tree produced by tsqlParser#file_spec.
    def enterFile_spec(self, ctx:tsqlParser.File_specContext):
        pass

    # Exit a parse tree produced by tsqlParser#file_spec.
    def exitFile_spec(self, ctx:tsqlParser.File_specContext):
        pass


    # Enter a parse tree produced by tsqlParser#full_table_name.
    def enterFull_table_name(self, ctx:tsqlParser.Full_table_nameContext):
        pass

    # Exit a parse tree produced by tsqlParser#full_table_name.
    def exitFull_table_name(self, ctx:tsqlParser.Full_table_nameContext):
        pass


    # Enter a parse tree produced by tsqlParser#table_name.
    def enterTable_name(self, ctx:tsqlParser.Table_nameContext):
        pass

    # Exit a parse tree produced by tsqlParser#table_name.
    def exitTable_name(self, ctx:tsqlParser.Table_nameContext):
        pass


    # Enter a parse tree produced by tsqlParser#simple_name.
    def enterSimple_name(self, ctx:tsqlParser.Simple_nameContext):
        pass

    # Exit a parse tree produced by tsqlParser#simple_name.
    def exitSimple_name(self, ctx:tsqlParser.Simple_nameContext):
        pass


    # Enter a parse tree produced by tsqlParser#func_proc_name.
    def enterFunc_proc_name(self, ctx:tsqlParser.Func_proc_nameContext):
        # print('enter func_proc_name', ctx)
        pass

    # Exit a parse tree produced by tsqlParser#func_proc_name.
    def exitFunc_proc_name(self, ctx:tsqlParser.Func_proc_nameContext):
        print('exit func_proc_name', ctx.getText())


    # Enter a parse tree produced by tsqlParser#ddl_object.
    def enterDdl_object(self, ctx:tsqlParser.Ddl_objectContext):
        pass

    # Exit a parse tree produced by tsqlParser#ddl_object.
    def exitDdl_object(self, ctx:tsqlParser.Ddl_objectContext):
        pass


    # Enter a parse tree produced by tsqlParser#full_column_name.
    def enterFull_column_name(self, ctx:tsqlParser.Full_column_nameContext):
        pass

    # Exit a parse tree produced by tsqlParser#full_column_name.
    def exitFull_column_name(self, ctx:tsqlParser.Full_column_nameContext):
        pass


    # Enter a parse tree produced by tsqlParser#column_name_list.
    def enterColumn_name_list(self, ctx:tsqlParser.Column_name_listContext):
        pass

    # Exit a parse tree produced by tsqlParser#column_name_list.
    def exitColumn_name_list(self, ctx:tsqlParser.Column_name_listContext):
        pass


    # Enter a parse tree produced by tsqlParser#cursor_name.
    def enterCursor_name(self, ctx:tsqlParser.Cursor_nameContext):
        pass

    # Exit a parse tree produced by tsqlParser#cursor_name.
    def exitCursor_name(self, ctx:tsqlParser.Cursor_nameContext):
        pass


    # Enter a parse tree produced by tsqlParser#on_off.
    def enterOn_off(self, ctx:tsqlParser.On_offContext):
        pass

    # Exit a parse tree produced by tsqlParser#on_off.
    def exitOn_off(self, ctx:tsqlParser.On_offContext):
        pass


    # Enter a parse tree produced by tsqlParser#clustered.
    def enterClustered(self, ctx:tsqlParser.ClusteredContext):
        pass

    # Exit a parse tree produced by tsqlParser#clustered.
    def exitClustered(self, ctx:tsqlParser.ClusteredContext):
        pass


    # Enter a parse tree produced by tsqlParser#null_notnull.
    def enterNull_notnull(self, ctx:tsqlParser.Null_notnullContext):
        pass

    # Exit a parse tree produced by tsqlParser#null_notnull.
    def exitNull_notnull(self, ctx:tsqlParser.Null_notnullContext):
        pass


    # Enter a parse tree produced by tsqlParser#scalar_function_name.
    def enterScalar_function_name(self, ctx:tsqlParser.Scalar_function_nameContext):
        pass

    # Exit a parse tree produced by tsqlParser#scalar_function_name.
    def exitScalar_function_name(self, ctx:tsqlParser.Scalar_function_nameContext):
        pass


    # Enter a parse tree produced by tsqlParser#data_type.
    def enterData_type(self, ctx:tsqlParser.Data_typeContext):
        pass

    # Exit a parse tree produced by tsqlParser#data_type.
    def exitData_type(self, ctx:tsqlParser.Data_typeContext):
        pass


    # Enter a parse tree produced by tsqlParser#default_value.
    def enterDefault_value(self, ctx:tsqlParser.Default_valueContext):
        pass

    # Exit a parse tree produced by tsqlParser#default_value.
    def exitDefault_value(self, ctx:tsqlParser.Default_valueContext):
        pass


    # Enter a parse tree produced by tsqlParser#constant.
    def enterConstant(self, ctx:tsqlParser.ConstantContext):
        pass

    # Exit a parse tree produced by tsqlParser#constant.
    def exitConstant(self, ctx:tsqlParser.ConstantContext):
        pass


    # Enter a parse tree produced by tsqlParser#sign.
    def enterSign(self, ctx:tsqlParser.SignContext):
        pass

    # Exit a parse tree produced by tsqlParser#sign.
    def exitSign(self, ctx:tsqlParser.SignContext):
        pass


    # Enter a parse tree produced by tsqlParser#id_var.
    def enterId_var(self, ctx:tsqlParser.Id_varContext):
        pass

    # Exit a parse tree produced by tsqlParser#id_var.
    def exitId_var(self, ctx:tsqlParser.Id_varContext):
        print('id', ctx.getText())


    # Enter a parse tree produced by tsqlParser#simple_id.
    def enterSimple_id(self, ctx:tsqlParser.Simple_idContext):
        # print('simple id', ctx)
        pass

    # Exit a parse tree produced by tsqlParser#simple_id.
    def exitSimple_id(self, ctx:tsqlParser.Simple_idContext):
        #print('simple_id', ctx.getText())
        pass


    # Enter a parse tree produced by tsqlParser#comparison_operator.
    def enterComparison_operator(self, ctx:tsqlParser.Comparison_operatorContext):
        pass

    # Exit a parse tree produced by tsqlParser#comparison_operator.
    def exitComparison_operator(self, ctx:tsqlParser.Comparison_operatorContext):
        pass


    # Enter a parse tree produced by tsqlParser#assignment_operator.
    def enterAssignment_operator(self, ctx:tsqlParser.Assignment_operatorContext):
        pass

    # Exit a parse tree produced by tsqlParser#assignment_operator.
    def exitAssignment_operator(self, ctx:tsqlParser.Assignment_operatorContext):
        pass


    # Enter a parse tree produced by tsqlParser#file_size.
    def enterFile_size(self, ctx:tsqlParser.File_sizeContext):
        pass

    # Exit a parse tree produced by tsqlParser#file_size.
    def exitFile_size(self, ctx:tsqlParser.File_sizeContext):
        pass

def parse(file_path):
    print("let's parse", file_path)
    input = FileStream(file_path, 'utf8')
    lexer = tsqlLexer(input)
    stream = CommonTokenStream(lexer)
    parser = tsqlParser(stream)
    tree = parser.tsql_file()
    printer = TsqlPrinter()
    walker = ParseTreeWalker()
    walker.walk(printer, tree)

def main(argv):
    for fp in argv[1:]:
        parse(fp)

if __name__ == '__main__':
    main(sys.argv)
