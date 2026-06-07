namespace Projet2
{
    partial class AddSessionForm
    {
        private System.ComponentModel.IContainer components = null;

        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null)) components.Dispose();
            base.Dispose(disposing);
        }

        #region Windows Form Designer generated code

        /// <summary>
        /// Required method for Designer support - do not modify
        /// the contents of this method with the code editor.
        /// </summary>
        private void InitializeComponent()
        {
            cbActivite = new System.Windows.Forms.ComboBox();
            numDuration = new System.Windows.Forms.NumericUpDown();
            dtpDate = new System.Windows.Forms.DateTimePicker();
            btnSave = new System.Windows.Forms.Button();
            label1 = new System.Windows.Forms.Label();
            ((System.ComponentModel.ISupportInitialize)numDuration).BeginInit();
            SuspendLayout();
            // 
            // cbActivite
            // 
            cbActivite.Location = new System.Drawing.Point(30, 30);
            cbActivite.Name = "cbActivite";
            cbActivite.Size = new System.Drawing.Size(200, 28);
            cbActivite.TabIndex = 0;
            // 
            // numDuration
            // 
            numDuration.Location = new System.Drawing.Point(146, 64);
            numDuration.Name = "numDuration";
            numDuration.Size = new System.Drawing.Size(100, 27);
            numDuration.TabIndex = 1;
            numDuration.ValueChanged += numDuration_ValueChanged;
            // 
            // dtpDate
            // 
            dtpDate.Location = new System.Drawing.Point(30, 110);
            dtpDate.Name = "dtpDate";
            dtpDate.Size = new System.Drawing.Size(238, 27);
            dtpDate.TabIndex = 2;
            // 
            // btnSave
            // 
            btnSave.Location = new System.Drawing.Point(30, 143);
            btnSave.Name = "btnSave";
            btnSave.Size = new System.Drawing.Size(96, 28);
            btnSave.TabIndex = 3;
            btnSave.Text = "Enregistrer";
            btnSave.Click += BtnSave_Click;
            // 
            // label1
            // 
            label1.Location = new System.Drawing.Point(35, 64);
            label1.Name = "label1";
            label1.Size = new System.Drawing.Size(105, 27);
            label1.TabIndex = 4;
            label1.Text = "durée en min";
            label1.TextAlign = System.Drawing.ContentAlignment.MiddleLeft;
            // 
            // AddSessionForm
            // 
            ClientSize = new System.Drawing.Size(300, 250);
            Controls.Add(label1);
            Controls.Add(cbActivite);
            Controls.Add(numDuration);
            Controls.Add(dtpDate);
            Controls.Add(btnSave);
            Text = "Ajouter une séance";
            ((System.ComponentModel.ISupportInitialize)numDuration).EndInit();
            ResumeLayout(false);
        }

        private System.Windows.Forms.Label label1;

        #endregion

        private System.Windows.Forms.ComboBox cbActivite;
        private System.Windows.Forms.NumericUpDown numDuration;
        private System.Windows.Forms.DateTimePicker dtpDate;
        private System.Windows.Forms.Button btnSave;
    }
}