const gulp = require('gulp')

const { spawn } = require('child_process')

let node







gulp.task('server', () => {

  if (node) node.kill()

  node = spawn('node', ['bin/www'], { stdio: 'inherit' })

  node.on('close', code => {

    if (code === 8) {

      gulp.log('Error detected, waiting for changes...')

    }

  })

})







gulp.task('default', ['server'], () => {

  gulp.watch([

    '**/*',

    '!node_modules/**/*',

    '!.editorconfig',

    '!.eslintrc',

    '!.gitignore',

    '!package-lock.json',

    '!package.json',

  ], ['server'])

})







process.on('exit', () => {

  if (node) node.kill()

})