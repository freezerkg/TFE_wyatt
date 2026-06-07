namespace Projet2;

partial class ProfileForm
{
    private System.ComponentModel.IContainer components = null;

    // Déclaration des contrôles
    private System.Windows.Forms.Label lblName;
    private System.Windows.Forms.TextBox txtName;
    private System.Windows.Forms.Label lblWeight;
    private System.Windows.Forms.NumericUpDown numWeight;
    private System.Windows.Forms.Label lblHeight;
    private System.Windows.Forms.NumericUpDown numHeight;
    private System.Windows.Forms.Label lblAge;
    private System.Windows.Forms.NumericUpDown numAge;
    private System.Windows.Forms.Label lblSex;
    private System.Windows.Forms.ComboBox cbSex;
    
    private System.Windows.Forms.GroupBox grpBmi;
    private System.Windows.Forms.Label lblBmiValue;
    private System.Windows.Forms.Label lblBmiCategory;

    private System.Windows.Forms.Button btnSave;
    private System.Windows.Forms.Button btnBack;

    protected override void Dispose(bool disposing)
    {
        if (disposing && (components != null))
        {
            components.Dispose();
        }
        base.Dispose(disposing);
    }

    #region Windows Form Designer generated code

    /// <summary>
    /// Required method for Designer support - do not modify
    /// the contents of this method with the code editor.
    /// </summary>
    private void InitializeComponent()
    {
        lblName = new System.Windows.Forms.Label();
        txtName = new System.Windows.Forms.TextBox();
        lblWeight = new System.Windows.Forms.Label();
        numWeight = new System.Windows.Forms.NumericUpDown();
        lblHeight = new System.Windows.Forms.Label();
        numHeight = new System.Windows.Forms.NumericUpDown();
        lblAge = new System.Windows.Forms.Label();
        numAge = new System.Windows.Forms.NumericUpDown();
        lblSex = new System.Windows.Forms.Label();
        cbSex = new System.Windows.Forms.ComboBox();
        grpBmi = new System.Windows.Forms.GroupBox();
        lblBmiValue = new System.Windows.Forms.Label();
        lblBmiCategory = new System.Windows.Forms.Label();
        btnSave = new System.Windows.Forms.Button();
        btnBack = new System.Windows.Forms.Button();
        ((System.ComponentModel.ISupportInitialize)numWeight).BeginInit();
        ((System.ComponentModel.ISupportInitialize)numHeight).BeginInit();
        ((System.ComponentModel.ISupportInitialize)numAge).BeginInit();
        grpBmi.SuspendLayout();
        SuspendLayout();
        // 
        // lblName
        // 
        lblName.Location = new System.Drawing.Point(30, 30);
        lblName.Name = "lblName";
        lblName.Size = new System.Drawing.Size(100, 23);
        lblName.TabIndex = 0;
        lblName.Text = "Nom :";
        // 
        // txtName
        // 
        txtName.Location = new System.Drawing.Point(136, 27);
        txtName.Name = "txtName";
        txtName.Size = new System.Drawing.Size(150, 27);
        txtName.TabIndex = 1;
        // 
        // lblWeight
        // 
        lblWeight.Location = new System.Drawing.Point(30, 70);
        lblWeight.Name = "lblWeight";
        lblWeight.Size = new System.Drawing.Size(100, 23);
        lblWeight.TabIndex = 2;
        lblWeight.Text = "Poids (kg) :";
        // 
        // numWeight
        // 
        numWeight.DecimalPlaces = 1;
        numWeight.Location = new System.Drawing.Point(136, 68);
        numWeight.Maximum = new decimal(new int[] { 300, 0, 0, 0 });
        numWeight.Name = "numWeight";
        numWeight.Size = new System.Drawing.Size(120, 27);
        numWeight.TabIndex = 3;
        // 
        // lblHeight
        // 
        lblHeight.Location = new System.Drawing.Point(30, 110);
        lblHeight.Name = "lblHeight";
        lblHeight.Size = new System.Drawing.Size(100, 23);
        lblHeight.TabIndex = 4;
        lblHeight.Text = "Taille (m) :";
        // 
        // numHeight
        // 
        numHeight.DecimalPlaces = 2;
        numHeight.Increment = new decimal(new int[] { 1, 0, 0, 131072 });
        numHeight.Location = new System.Drawing.Point(136, 106);
        numHeight.Maximum = new decimal(new int[] { 3, 0, 0, 0 });
        numHeight.Name = "numHeight";
        numHeight.Size = new System.Drawing.Size(120, 27);
        numHeight.TabIndex = 5;
        // 
        // lblAge
        // 
        lblAge.Location = new System.Drawing.Point(30, 150);
        lblAge.Name = "lblAge";
        lblAge.Size = new System.Drawing.Size(100, 23);
        lblAge.TabIndex = 6;
        lblAge.Text = "Âge :";
        // 
        // numAge
        // 
        numAge.Location = new System.Drawing.Point(136, 146);
        numAge.Name = "numAge";
        numAge.Size = new System.Drawing.Size(120, 27);
        numAge.TabIndex = 7;
        // 
        // lblSex
        // 
        lblSex.Location = new System.Drawing.Point(30, 190);
        lblSex.Name = "lblSex";
        lblSex.Size = new System.Drawing.Size(100, 23);
        lblSex.TabIndex = 8;
        lblSex.Text = "Sexe :";
        // 
        // cbSex
        // 
        cbSex.DropDownStyle = System.Windows.Forms.ComboBoxStyle.DropDownList;
        cbSex.Items.AddRange(new object[] { "M", "F" });
        cbSex.Location = new System.Drawing.Point(136, 185);
        cbSex.Name = "cbSex";
        cbSex.Size = new System.Drawing.Size(121, 28);
        cbSex.TabIndex = 9;
        // 
        // grpBmi
        // 
        grpBmi.Controls.Add(lblBmiValue);
        grpBmi.Controls.Add(lblBmiCategory);
        grpBmi.Location = new System.Drawing.Point(300, 27);
        grpBmi.Name = "grpBmi";
        grpBmi.Size = new System.Drawing.Size(200, 188);
        grpBmi.TabIndex = 10;
        grpBmi.TabStop = false;
        grpBmi.Text = "Indice de Masse Corporelle";
        // 
        // lblBmiValue
        // 
        lblBmiValue.Font = new System.Drawing.Font("Segoe UI", 16F, System.Drawing.FontStyle.Bold);
        lblBmiValue.Location = new System.Drawing.Point(20, 50);
        lblBmiValue.Name = "lblBmiValue";
        lblBmiValue.Size = new System.Drawing.Size(160, 40);
        lblBmiValue.TabIndex = 0;
        lblBmiValue.Text = "--";
        lblBmiValue.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
        // 
        // lblBmiCategory
        // 
        lblBmiCategory.Location = new System.Drawing.Point(20, 100);
        lblBmiCategory.Name = "lblBmiCategory";
        lblBmiCategory.Size = new System.Drawing.Size(160, 30);
        lblBmiCategory.TabIndex = 1;
        lblBmiCategory.Text = "Catégorie inconnue";
        lblBmiCategory.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
        // 
        // btnSave
        // 
        btnSave.Location = new System.Drawing.Point(300, 240);
        btnSave.Name = "btnSave";
        btnSave.Size = new System.Drawing.Size(200, 40);
        btnSave.TabIndex = 11;
        btnSave.Text = "Enregistrer le profil";
        // 
        // btnBack
        // 
        btnBack.Location = new System.Drawing.Point(30, 240);
        btnBack.Name = "btnBack";
        btnBack.Size = new System.Drawing.Size(120, 40);
        btnBack.TabIndex = 12;
        btnBack.Text = "Retour";
        // 
        // ProfileForm
        // 
        ClientSize = new System.Drawing.Size(530, 310);
        Controls.Add(lblName);
        Controls.Add(txtName);
        Controls.Add(lblWeight);
        Controls.Add(numWeight);
        Controls.Add(lblHeight);
        Controls.Add(numHeight);
        Controls.Add(lblAge);
        Controls.Add(numAge);
        Controls.Add(lblSex);
        Controls.Add(cbSex);
        Controls.Add(grpBmi);
        Controls.Add(btnSave);
        Controls.Add(btnBack);
        StartPosition = System.Windows.Forms.FormStartPosition.CenterScreen;
        Text = "Profil Utilisateur";
        ((System.ComponentModel.ISupportInitialize)numWeight).EndInit();
        ((System.ComponentModel.ISupportInitialize)numHeight).EndInit();
        ((System.ComponentModel.ISupportInitialize)numAge).EndInit();
        grpBmi.ResumeLayout(false);
        ResumeLayout(false);
        PerformLayout();
    }

    #endregion
}